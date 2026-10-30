package com.myrnd.opencode

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.app.Service
import android.content.Context
import android.content.Intent
import android.os.IBinder
import android.os.PowerManager
import android.util.Log
import java.security.SecureRandom
import java.util.Base64
import kotlin.concurrent.thread

/** Keeps the OpenCode server alive in the background, restarting it a few times if it crashes. */
class OpenCodeService : Service() {
    companion object {
        private const val TAG = "OpenCodeService"
        private const val ACTION_STOP = "com.myrnd.opencode.STOP"
        private const val CHANNEL = "server"
        private const val MAX_RESTARTS = 3
        private const val RESTART_WINDOW_MS = 120_000L

        /** True once the server crashed [MAX_RESTARTS] times in a row; cleared on the next start. */
        @Volatile
        var gaveUp = false
            private set

        /** Password of the running server; a new one is made on every start, so old sessions stop working. */
        @Volatile
        var password: String? = null
            private set

        @Volatile
        var serverAlive = false
            private set

        fun start(context: Context) {
            gaveUp = false
            context.startForegroundService(Intent(context, OpenCodeService::class.java))
        }
    }

    private lateinit var runtime: OpenCodeRuntime
    private var wakeLock: PowerManager.WakeLock? = null

    @Volatile
    private var process: Process? = null
    private var loop: Thread? = null

    @Volatile
    private var stopping = false
    private val crashes = ArrayDeque<Long>()

    override fun onCreate() {
        super.onCreate()
        runtime = OpenCodeRuntime(this)
        getSystemService(NotificationManager::class.java)
            .createNotificationChannel(NotificationChannel(CHANNEL, "OpenCode server", NotificationManager.IMPORTANCE_LOW))
        // Agent runs keep going with the screen off.
        wakeLock = getSystemService(PowerManager::class.java)
            .newWakeLock(PowerManager.PARTIAL_WAKE_LOCK, "opencode:server")
            .apply { acquire() }
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        if (intent?.action == ACTION_STOP) {
            stopping = true
            process?.destroy()
            stopForeground(STOP_FOREGROUND_REMOVE)
            stopSelf()
            return START_NOT_STICKY
        }
        startForeground(1, notification())
        if (loop?.isAlive != true) launch()
        return START_STICKY
    }

    private fun launch() {
        stopping = false
        loop = thread(name = "opencode-server") {
            while (!stopping) {
                val exit = runCatching {
                    val fresh = ByteArray(32).also { SecureRandom().nextBytes(it) }
                        .let { Base64.getUrlEncoder().withoutPadding().encodeToString(it) }
                    val started = runtime.startServer(fresh)
                    password = fresh
                    process = started
                    serverAlive = true
                    started.waitFor()
                }.onFailure { Log.e(TAG, "Could not start OpenCode server", it) }.getOrNull()
                serverAlive = false
                if (stopping) break
                Log.w(TAG, "OpenCode server exited with code $exit")
                runCatching { runtime.serverLog.appendText("=== server exited with code $exit ===\n") }
                    .onFailure { Log.e(TAG, "Could not write to the server log", it) }
                val now = System.currentTimeMillis()
                crashes.addLast(now)
                while (crashes.isNotEmpty() && now - crashes.first() > RESTART_WINDOW_MS) crashes.removeFirst()
                if (crashes.size > MAX_RESTARTS) {
                    Log.e(TAG, "OpenCode server crashed ${crashes.size} times in ${RESTART_WINDOW_MS / 1000}s; giving up")
                    gaveUp = true
                    stopSelf()
                    break
                }
                Thread.sleep(2000)
            }
        }
    }

    private fun notification(): Notification {
        val open = PendingIntent.getActivity(
            this, 0, Intent(this, MainActivity::class.java), PendingIntent.FLAG_IMMUTABLE,
        )
        val stop = PendingIntent.getService(
            this, 1, Intent(this, OpenCodeService::class.java).setAction(ACTION_STOP), PendingIntent.FLAG_IMMUTABLE,
        )
        return Notification.Builder(this, CHANNEL)
            .setSmallIcon(R.drawable.ic_notification)
            .setContentTitle("OpenCode is running")
            .setContentText("Local server on this phone")
            .setContentIntent(open)
            .setOngoing(true)
            .addAction(Notification.Action.Builder(null, "Stop", stop).build())
            .build()
    }

    override fun onDestroy() {
        stopping = true
        serverAlive = false
        password = null
        process?.destroy()
        wakeLock?.release()
        super.onDestroy()
    }

    override fun onBind(intent: Intent?): IBinder? = null
}
