package com.myrnd.opencode.core

/**
 * Our server is ready once its own output (since its latest start) says it bound the port. Only one process can
 * listen on the port, so this proves no other app took it before the password is sent to it.
 */
object ServerReadiness {
    const val START_PREFIX = "=== server start"

    fun startMarker(time: String) = "$START_PREFIX $time ==="

    fun listening(log: String, port: Int): Boolean {
        val start = log.lastIndexOf(START_PREFIX)
        if (start < 0) return false
        return log.substring(start).contains("server listening on http://127.0.0.1:$port")
    }
}
