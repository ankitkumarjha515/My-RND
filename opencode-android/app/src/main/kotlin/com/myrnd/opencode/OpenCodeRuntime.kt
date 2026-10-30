package com.myrnd.opencode

import android.Manifest
import android.content.Context
import android.content.pm.PackageManager
import android.os.Build
import android.os.Environment
import com.myrnd.opencode.core.ProotCommand
import com.myrnd.opencode.core.ServerReadiness
import com.myrnd.opencode.core.TarExtractor
import java.io.File
import java.io.RandomAccessFile
import java.nio.file.Files
import java.util.Date

/** Owns the on-device Linux: unpacking Alpine, first-run setup, and launching commands inside it through proot. */
class OpenCodeRuntime(private val context: Context) {
    companion object {
        const val PORT = 4096
        const val BASE_URL = "http://127.0.0.1:$PORT"
        private const val OPENCODE = "/usr/local/bin/opencode"
        private const val SETUP_SCRIPT = "/.opencode/setup.sh"
        // Only this folder of shared storage is visible to the agent, never the whole phone.
        private const val STORAGE_FOLDER = "/storage/emulated/0/OpenCode"
        private const val PASSWORD_FILE = "/.opencode/server-password"
        private const val MAX_LOG_BYTES = 1_000_000L
        private const val READY_TAIL_BYTES = 64 * 1024
    }

    private val files = context.filesDir
    private val nativeDir = File(context.applicationInfo.nativeLibraryDir)
    private val rootfs = File(files, "alpine")
    private val tmp = File(files, "tmp")
    private val lib = File(files, "lib")
    private val state = File(rootfs, ".opencode")
    private val rootfsReady = File(state, "rootfs-ready")
    private val setupDone = File(state, "setup-done")
    val serverLog = File(files, "server.log")

    init {
        // Earlier builds kept one permanent password here; it now changes on every server start and lives in memory.
        context.getSharedPreferences("opencode", Context.MODE_PRIVATE).edit().remove("server_password").apply()
    }

    fun isSetUp() = setupDone.exists()

    fun resetSetup() {
        setupDone.delete()
    }

    fun hasStorageAccess() =
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) Environment.isExternalStorageManager()
        else context.checkSelfPermission(Manifest.permission.WRITE_EXTERNAL_STORAGE) == PackageManager.PERMISSION_GRANTED

    /** Unpacks Alpine (once) and installs git, ripgrep, bash and OpenCode inside it. Needs internet. */
    fun setUp(log: (String) -> Unit) {
        prepareHost()
        if (!rootfsReady.exists()) {
            log("Unpacking Linux…")
            rootfs.deleteRecursively()
            rootfs.mkdirs()
            context.assets.open("alpine-rootfs.bin").use { TarExtractor.extractTarGz(it, rootfs) }
            state.mkdirs()
            rootfsReady.createNewFile()
        }
        prepareGuest()
        context.assets.open("setup.sh").use { input -> File(rootfs, SETUP_SCRIPT).outputStream().use { input.copyTo(it) } }
        val process = process(listOf("/bin/sh", SETUP_SCRIPT)).redirectErrorStream(true).start()
        process.inputStream.bufferedReader().forEachLine(log)
        val code = process.waitFor()
        if (code != 0) throw IllegalStateException("Setup failed (exit code $code). Check your internet connection and tap Retry.")
        setupDone.createNewFile()
    }

    /** Starts `opencode serve` on loopback; its output is appended to [serverLog] so earlier crashes stay visible. */
    fun startServer(password: String): Process {
        prepareHost()
        prepareGuest()
        if (serverLog.length() > MAX_LOG_BYTES) serverLog.writeText(serverLogTail(200) + "\n")
        serverLog.appendText("\n${ServerReadiness.startMarker(Date().toString())}\n")
        // Hand the password over in a private file the server reads and deletes, so it never appears on a command line.
        File(rootfs, PASSWORD_FILE).apply {
            writeText(password)
            setReadable(false, false)
            setReadable(true, true)
        }
        val serve = "$OPENCODE serve --hostname 127.0.0.1 --port $PORT"
        return process(
            listOf("/bin/sh", "-c", "OPENCODE_PASSWORD=\"\$(cat $PASSWORD_FILE)\" && rm -f $PASSWORD_FILE && export OPENCODE_PASSWORD && exec $serve"),
        ).redirectErrorStream(true).redirectOutput(ProcessBuilder.Redirect.appendTo(serverLog)).start()
    }

    /** True once the server we started last reports it bound the port (see [ServerReadiness]). */
    fun serverListening(): Boolean {
        if (!serverLog.exists()) return false
        val tail = RandomAccessFile(serverLog, "r").use { file ->
            val start = maxOf(0L, file.length() - READY_TAIL_BYTES)
            ByteArray((file.length() - start).toInt()).also { file.seek(start); file.readFully(it) }
        }
        return ServerReadiness.listening(String(tail), PORT)
    }

    fun serverLogTail(lines: Int = 40) =
        if (serverLog.exists()) serverLog.readLines().takeLast(lines).joinToString("\n") else ""

    private fun prepareHost() {
        val proot = File(nativeDir, "libproot.so")
        if (!proot.exists()) throw IllegalStateException("This APK was built without proot. Rebuild it with scripts/fetch-native.sh.")
        tmp.mkdirs()
        lib.mkdirs()
        // proot is linked against libtalloc.so.2; the APK can only ship it as libtalloc.so, and its directory moves on updates.
        val talloc = File(lib, "libtalloc.so.2").toPath()
        Files.deleteIfExists(talloc)
        Files.createSymbolicLink(talloc, File(nativeDir, "libtalloc.so").toPath())
    }

    private fun prepareGuest() {
        state.mkdirs()
        File(rootfs, "tmp").mkdirs()
        File(rootfs, "root/projects").mkdirs()
        // Android has no /etc/resolv.conf for Linux programs to read.
        File(rootfs, "etc/resolv.conf").writeText("nameserver 8.8.8.8\nnameserver 1.1.1.1\n")
        val fakeProc = File(state, "proc").apply { mkdirs() }
        ProotCommand.FAKE_PROC.forEach { (name, content) -> File(fakeProc, name).writeText(content) }
    }

    private fun process(command: List<String>, extraEnv: Map<String, String> = emptyMap()): ProcessBuilder {
        val fakeProcBinds = ProotCommand.fakeProcBinds(File(state, "proc").path) { runCatching { File(it).readText() }.isSuccess }
        val storageBinds =
            if (hasStorageAccess() && File(STORAGE_FOLDER).apply { mkdirs() }.isDirectory) listOf(ProotCommand.Bind(STORAGE_FOLDER, "/sdcard"))
            else emptyList()
        val config = ProotCommand.Config(
            proot = File(nativeDir, "libproot.so").path,
            loader = File(nativeDir, "libproot-loader.so").path,
            // libtalloc.so.2 is a symlink in lib; libandroid-shmem.so keeps its own name in the APK's library dir.
            libraryDir = "${lib.path}:${nativeDir.path}",
            tmpDir = tmp.path,
            rootfs = rootfs.path,
            workdir = "/root/projects",
            binds = fakeProcBinds + storageBinds,
            env = mapOf(
                "HOME" to "/root",
                "USER" to "root",
                "PATH" to "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
                "SHELL" to "/bin/bash",
                "TERM" to "xterm-256color",
                "LANG" to "C.UTF-8",
                "TMPDIR" to "/tmp",
            ) + extraEnv,
        )
        return ProcessBuilder(ProotCommand.argv(config, command)).directory(files).also {
            it.environment().clear()
            it.environment().putAll(ProotCommand.hostEnv(config))
        }
    }
}
