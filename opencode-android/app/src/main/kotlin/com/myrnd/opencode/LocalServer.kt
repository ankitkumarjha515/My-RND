package com.myrnd.opencode

import com.myrnd.opencode.core.Pairing
import java.net.HttpURLConnection
import java.net.URL

/** Talks to the OpenCode server running on the phone. */
object LocalServer {
    fun healthy() = runCatching {
        val connection = URL(OpenCodeRuntime.BASE_URL).openConnection() as HttpURLConnection
        connection.connectTimeout = 1000
        connection.readTimeout = 2000
        try {
            connection.responseCode == 200
        } finally {
            connection.disconnect()
        }
    }.getOrDefault(false)

    /** Waits for the server, then returns a single-use sign-in link for the WebView. */
    fun waitAndPair(password: String, timeoutMs: Long, failed: () -> Boolean): String {
        val deadline = System.currentTimeMillis() + timeoutMs
        while (!healthy()) {
            if (failed()) throw IllegalStateException("OpenCode server keeps crashing.")
            if (System.currentTimeMillis() > deadline) throw IllegalStateException("OpenCode server did not start within ${timeoutMs / 1000}s.")
            Thread.sleep(500)
        }
        val connection = URL("${OpenCodeRuntime.BASE_URL}/api/pair").openConnection() as HttpURLConnection
        try {
            connection.requestMethod = "POST"
            connection.setRequestProperty("Authorization", Pairing.basicAuth(password))
            connection.connectTimeout = 2000
            connection.readTimeout = 5000
            val code = connection.responseCode
            val body = (if (code in 200..299) connection.inputStream else connection.errorStream)?.bufferedReader()?.readText().orEmpty()
            if (code !in 200..299) throw IllegalStateException("Sign-in to the local server failed (HTTP $code): $body")
            return Pairing.connectUrl(OpenCodeRuntime.BASE_URL, Pairing.code(body))
        } finally {
            connection.disconnect()
        }
    }
}
