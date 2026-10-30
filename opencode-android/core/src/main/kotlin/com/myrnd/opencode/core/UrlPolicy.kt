package com.myrnd.opencode.core

/** What the WebView may load. Cookies are not port-isolated, so only our exact server origin is trusted. */
object UrlPolicy {
    private val LOOPBACK_HOSTS = setOf("127.0.0.1", "localhost", "[::1]", "::1")

    fun isOurServer(scheme: String?, host: String?, port: Int, serverPort: Int) =
        scheme == "http" && host == "127.0.0.1" && port == serverPort

    /** Another app's local server: never load it in the WebView, where it would receive our session cookie. */
    fun isOtherLoopback(host: String?, port: Int, serverPort: Int) =
        host in LOOPBACK_HOSTS && !(host == "127.0.0.1" && port == serverPort)

    /** Only real web links the user tapped go to the browser; scripts cannot launch other apps. */
    fun mayOpenExternally(scheme: String?, host: String?, userTapped: Boolean) =
        userTapped && (scheme == "http" || scheme == "https") && host !in LOOPBACK_HOSTS
}
