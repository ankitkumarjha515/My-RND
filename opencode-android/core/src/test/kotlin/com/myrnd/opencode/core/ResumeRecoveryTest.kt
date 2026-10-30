package com.myrnd.opencode.core

import com.myrnd.opencode.core.ResumeRecovery.Action
import org.junit.Assert.assertEquals
import org.junit.Test

class ResumeRecoveryTest {
    @Test
    fun restartsWhenServerIsDown() {
        assertEquals(Action.RESTART, ResumeRecovery.decide(serverHealthy = false, pageText = "Home"))
    }

    @Test
    fun reloadsWhenPageIsBlank() {
        assertEquals(Action.RELOAD, ResumeRecovery.decide(serverHealthy = true, pageText = "\"\""))
        assertEquals(Action.RELOAD, ResumeRecovery.decide(serverHealthy = true, pageText = "\"   \""))
    }

    @Test
    fun reloadsWhenPageCannotRunScripts() {
        assertEquals(Action.RELOAD, ResumeRecovery.decide(serverHealthy = true, pageText = null))
        assertEquals(Action.RELOAD, ResumeRecovery.decide(serverHealthy = true, pageText = "null"))
    }

    @Test
    fun leavesAWorkingPageAlone() {
        assertEquals(Action.NONE, ResumeRecovery.decide(serverHealthy = true, pageText = "\"Home All projects\""))
    }
}
