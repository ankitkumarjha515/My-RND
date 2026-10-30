package com.myrnd.opencode.core

import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class UrlPolicyTest {
    @Test
    fun onlyTheLocalServerPortCountsAsOurServer() {
        assertTrue(UrlPolicy.isOurServer("http", "127.0.0.1", 4096, 4096))
        assertFalse(UrlPolicy.isOurServer("http", "127.0.0.1", 8080, 4096))
        assertFalse(UrlPolicy.isOurServer("http", "127.0.0.1", -1, 4096))
        assertFalse(UrlPolicy.isOurServer("https", "127.0.0.1", 4096, 4096))
        assertFalse(UrlPolicy.isOurServer("http", "localhost", 4096, 4096))
    }

    @Test
    fun otherLoopbackPortsAreBlocked() {
        assertTrue(UrlPolicy.isOtherLoopback("127.0.0.1", 8080, 4096))
        assertTrue(UrlPolicy.isOtherLoopback("localhost", 4096, 4096))
        assertTrue(UrlPolicy.isOtherLoopback("[::1]", 4096, 4096))
        assertFalse(UrlPolicy.isOtherLoopback("127.0.0.1", 4096, 4096))
        assertFalse(UrlPolicy.isOtherLoopback("example.com", 80, 4096))
    }

    @Test
    fun externalLinksNeedATapAndAWebScheme() {
        assertTrue(UrlPolicy.mayOpenExternally("https", "github.com", userTapped = true))
        assertTrue(UrlPolicy.mayOpenExternally("http", "example.com", userTapped = true))
        assertFalse(UrlPolicy.mayOpenExternally("https", "github.com", userTapped = false))
        assertFalse(UrlPolicy.mayOpenExternally("tel", null, userTapped = true))
        assertFalse(UrlPolicy.mayOpenExternally("intent", null, userTapped = true))
        assertFalse(UrlPolicy.mayOpenExternally("http", "127.0.0.1", userTapped = true))
    }
}
