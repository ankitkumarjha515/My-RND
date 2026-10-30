package com.myrnd.opencode.core

import org.junit.Assert.assertEquals
import org.junit.Assert.assertThrows
import org.junit.Test

class PairingTest {
    @Test
    fun readsCodeFromServerResponse() {
        assertEquals("m31KVLDygWuT1mI9Xy1paA", Pairing.code("""{"code":"m31KVLDygWuT1mI9Xy1paA","expires_in":300}"""))
    }

    @Test
    fun rejectsResponseWithoutCode() {
        assertThrows(IllegalStateException::class.java) { Pairing.code("""{"_tag":"UnauthorizedError"}""") }
    }

    @Test
    fun buildsConnectUrlAndBasicHeader() {
        assertEquals("http://127.0.0.1:4096/auth/connect/abc", Pairing.connectUrl("http://127.0.0.1:4096", "abc"))
        assertEquals("Basic b3BlbmNvZGU6cHc=", Pairing.basicAuth("pw"))
    }
}
