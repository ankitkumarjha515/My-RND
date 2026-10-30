package com.myrnd.opencode.core

import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class ServerReadinessTest {
    private val start = "=== server start Thu Oct 30 10:00:00 IST 2026 ==="

    @Test
    fun readyWhenOurLatestStartIsListening() {
        assertTrue(ServerReadiness.listening("$start\nserver listening on http://127.0.0.1:4096\n", 4096))
    }

    @Test
    fun notReadyWhenOurServerCouldNotBind() {
        val log = "$start\nserver listening on http://127.0.0.1:4096\n=== server exited with code 1 ===\n" +
            "$start\nError: listen EADDRINUSE 127.0.0.1:4096\n"
        assertFalse(ServerReadiness.listening(log, 4096))
    }

    @Test
    fun notReadyBeforeAnyStartOrOnAnotherPort() {
        assertFalse(ServerReadiness.listening("server listening on http://127.0.0.1:4096\n", 4096))
        assertFalse(ServerReadiness.listening("$start\nserver listening on http://127.0.0.1:5000\n", 4096))
    }

    @Test
    fun markerMatchesWhatTheRuntimeWrites() {
        assertTrue(ServerReadiness.startMarker("now").contains(ServerReadiness.START_PREFIX))
    }
}
