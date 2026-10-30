package com.myrnd.opencode

import android.Manifest
import android.app.Activity
import android.content.ActivityNotFoundException
import android.content.Intent
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.provider.Settings
import android.util.Log
import android.view.View
import android.view.ViewGroup
import android.webkit.HttpAuthHandler
import android.webkit.RenderProcessGoneDetail
import android.webkit.WebChromeClient
import android.webkit.WebResourceError
import android.webkit.WebResourceRequest
import android.webkit.WebResourceResponse
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.Button
import android.widget.ProgressBar
import android.widget.TextView
import com.myrnd.opencode.core.ResumeRecovery
import com.myrnd.opencode.core.UrlPolicy
import java.io.ByteArrayInputStream
import kotlin.concurrent.thread

/** Shows first-run setup progress, then OpenCode's own web UI served from the phone. */
class MainActivity : Activity() {
    companion object {
        private const val TAG = "MainActivity"
        private const val SERVER_START_TIMEOUT_MS = 120_000L
        private const val LOG_LINES = 200
        private const val PAGE_CHECK_TIMEOUT_MS = 3000L
    }

    private lateinit var runtime: OpenCodeRuntime
    private lateinit var web: WebView
    private lateinit var statusPanel: View
    private lateinit var status: TextView
    private lateinit var progress: ProgressBar
    private lateinit var actions: View
    private lateinit var storage: Button
    private lateinit var log: TextView
    private val logLines = ArrayDeque<String>()
    private var starting = false

    /** The server password the WebView's session was issued under; a different one means the server restarted. */
    private var pairedPassword: String? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        runtime = OpenCodeRuntime(this)
        web = findViewById(R.id.web)
        statusPanel = findViewById(R.id.status_panel)
        status = findViewById(R.id.status)
        progress = findViewById(R.id.progress)
        actions = findViewById(R.id.actions)
        storage = findViewById(R.id.storage)
        log = findViewById(R.id.log)
        findViewById<Button>(R.id.retry).setOnClickListener { start() }
        findViewById<Button>(R.id.rerun_setup).setOnClickListener {
            runtime.resetSetup()
            start()
        }
        storage.setOnClickListener { requestStorage() }
        setUpWebView()
        start()
    }

    override fun onResume() {
        super.onResume()
        storage.visibility = if (runtime.hasStorageAccess()) View.GONE else View.VISIBLE
        if (web.visibility == View.VISIBLE && OpenCodeService.password != pairedPassword) start()
        else if (web.visibility == View.VISIBLE) thread {
            val healthy = LocalServer.healthy()
            runOnUiThread { recoverPage(healthy) }
        }
    }

    // After time in the background the server may have been stopped (notification, Android) or the page left blank.
    private fun recoverPage(serverHealthy: Boolean) {
        var answered = false
        val check = { text: String? ->
            if (!answered) {
                answered = true
                val action = ResumeRecovery.decide(serverHealthy, text)
                Log.i(TAG, "Resume check: server healthy=$serverHealthy, action=$action")
                when (action) {
                    ResumeRecovery.Action.RESTART -> start()
                    ResumeRecovery.Action.RELOAD -> web.reload()
                    ResumeRecovery.Action.NONE -> Unit
                }
            }
        }
        web.evaluateJavascript("document.body ? document.body.innerText : ''") { check(it) }
        // A page that cannot run scripts never answers.
        web.postDelayed({ check(null) }, PAGE_CHECK_TIMEOUT_MS)
    }

    @Deprecated("Deprecated in Java")
    override fun onBackPressed() {
        if (web.visibility == View.VISIBLE && web.canGoBack()) web.goBack() else super.onBackPressed()
    }

    private fun setUpWebView() {
        web.settings.javaScriptEnabled = true
        web.settings.domStorageEnabled = true
        web.settings.allowFileAccess = false
        web.settings.allowContentAccess = false
        web.webChromeClient = WebChromeClient()
        web.webViewClient = object : WebViewClient() {
            override fun shouldOverrideUrlLoading(view: WebView, request: WebResourceRequest): Boolean {
                val url = request.url
                if (UrlPolicy.isOurServer(url.scheme, url.host, url.port, OpenCodeRuntime.PORT)) return false
                if (!UrlPolicy.mayOpenExternally(url.scheme, url.host, request.hasGesture())) {
                    Log.w(TAG, "Blocked navigation to $url")
                    return true
                }
                try {
                    startActivity(Intent(Intent.ACTION_VIEW, url))
                } catch (e: ActivityNotFoundException) {
                    Log.w(TAG, "No app can open $url", e)
                }
                return true
            }

            // WebView cookies are shared by every port on 127.0.0.1, so requests to other local servers are refused.
            override fun shouldInterceptRequest(view: WebView, request: WebResourceRequest): WebResourceResponse? {
                val url = request.url
                if (!UrlPolicy.isOtherLoopback(url.host, url.port, OpenCodeRuntime.PORT)) return null
                Log.w(TAG, "Blocked request to another local server: $url")
                return WebResourceResponse("text/plain", "utf-8", 403, "Forbidden", emptyMap(), ByteArrayInputStream(ByteArray(0)))
            }

            // Sign-in only happens through the pairing link; credentials are never typed into an auth prompt.
            override fun onReceivedHttpAuthRequest(view: WebView, handler: HttpAuthHandler, host: String, realm: String) {
                handler.cancel()
            }

            override fun onReceivedError(view: WebView, request: WebResourceRequest, error: WebResourceError) {
                if (request.isForMainFrame) showError(IllegalStateException("The page failed to load: ${error.description}"))
            }

            // Android kills the page's renderer to free memory while the app is in the background. Without this the
            // WebView stays blank (or the app crashes); a dead WebView cannot be reused, so swap in a new one.
            override fun onRenderProcessGone(view: WebView, detail: RenderProcessGoneDetail): Boolean {
                Log.w(TAG, "WebView renderer gone (crashed=${detail.didCrash()}); recreating it")
                replaceWebView()
                start()
                return true
            }
        }
    }

    private fun replaceWebView() {
        val parent = web.parent as ViewGroup
        val index = parent.indexOfChild(web)
        val params = web.layoutParams
        parent.removeView(web)
        web.destroy()
        web = WebView(this).apply { visibility = View.GONE }
        parent.addView(web, index, params)
        setUpWebView()
    }

    private fun start() {
        if (starting) return
        starting = true
        logLines.clear()
        showStatus(if (runtime.isSetUp()) "Starting OpenCode…" else "Setting up OpenCode. First run only; needs internet and takes a few minutes.")
        thread(name = "opencode-start") {
            val result = runCatching {
                if (!runtime.isSetUp()) runtime.setUp(::appendLog)
                runOnUiThread { status.text = "Starting OpenCode…" }
                OpenCodeService.start(this)
                LocalServer.waitAndPair(
                    password = { OpenCodeService.password },
                    timeoutMs = SERVER_START_TIMEOUT_MS,
                    ready = { OpenCodeService.serverAlive && runtime.serverListening() },
                    failed = { OpenCodeService.gaveUp },
                )
            }
            runOnUiThread {
                starting = false
                result.fold({ (url, password) ->
                    pairedPassword = password
                    showWeb(url)
                }, ::showError)
            }
        }
    }

    private fun showStatus(message: String) {
        web.visibility = View.GONE
        statusPanel.visibility = View.VISIBLE
        status.text = message
        progress.visibility = View.VISIBLE
        actions.visibility = View.GONE
        log.text = ""
    }

    private fun showWeb(signInUrl: String) {
        statusPanel.visibility = View.GONE
        web.visibility = View.VISIBLE
        web.loadUrl(signInUrl)
    }

    private fun showError(error: Throwable) {
        Log.e(TAG, "OpenCode failed to start", error)
        web.visibility = View.GONE
        statusPanel.visibility = View.VISIBLE
        progress.visibility = View.GONE
        actions.visibility = View.VISIBLE
        status.text = "Couldn't start OpenCode: ${error.message ?: error.javaClass.simpleName}"
        val serverLog = runtime.serverLogTail()
        log.text = listOf(logLines.joinToString("\n"), if (serverLog.isEmpty()) "" else "--- server log ---\n$serverLog")
            .filter { it.isNotEmpty() }
            .joinToString("\n\n")
    }

    private fun appendLog(line: String) {
        runOnUiThread {
            logLines.addLast(line)
            while (logLines.size > LOG_LINES) logLines.removeFirst()
            log.text = logLines.joinToString("\n")
        }
    }

    private fun requestStorage() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
            try {
                startActivity(Intent(Settings.ACTION_MANAGE_APP_ALL_FILES_ACCESS_PERMISSION, Uri.parse("package:$packageName")))
            } catch (e: ActivityNotFoundException) {
                Log.w(TAG, "Per-app all-files settings missing; opening the general list", e)
                startActivity(Intent(Settings.ACTION_MANAGE_ALL_FILES_ACCESS_PERMISSION))
            }
        } else {
            requestPermissions(arrayOf(Manifest.permission.READ_EXTERNAL_STORAGE, Manifest.permission.WRITE_EXTERNAL_STORAGE), 1)
        }
    }
}
