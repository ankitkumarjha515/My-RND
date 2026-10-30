package com.myrnd.opencode.core

/** Decides how to bring the UI back when the app returns from the background. */
object ResumeRecovery {
    enum class Action { NONE, RELOAD, RESTART }

    /** [pageText] is the JSON string WebView's evaluateJavascript returns for `document.body.innerText`. */
    fun decide(serverHealthy: Boolean, pageText: String?) = when {
        !serverHealthy -> Action.RESTART
        pageText == null || pageText == "null" -> Action.RELOAD
        pageText.trim('"').isBlank() -> Action.RELOAD
        else -> Action.NONE
    }
}
