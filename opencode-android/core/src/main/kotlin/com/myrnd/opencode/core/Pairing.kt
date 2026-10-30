package com.myrnd.opencode.core

import java.util.Base64

/** Signs the WebView in through OpenCode's single-use pairing link, which sets the server's session cookie. */
object Pairing {
    const val USERNAME = "opencode"
    private val CODE = Regex("\"code\"\\s*:\\s*\"([A-Za-z0-9_-]+)\"")

    fun code(response: String) =
        CODE.find(response)?.groupValues?.get(1) ?: throw IllegalStateException("No pairing code in server response: $response")

    fun connectUrl(base: String, code: String) = "$base/auth/connect/$code"

    fun basicAuth(password: String) =
        "Basic " + Base64.getEncoder().encodeToString("$USERNAME:$password".toByteArray())
}
