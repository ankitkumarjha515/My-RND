pluginManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
    plugins {
        id("com.android.application") version "8.7.3"
        id("org.jetbrains.kotlin.android") version "2.0.21"
        id("org.jetbrains.kotlin.jvm") version "2.0.21"
    }
}

dependencyResolutionManagement {
    repositories {
        google()
        mavenCentral()
    }
}

rootProject.name = "opencode-android"
include(":core")
// The Android SDK is only available in CI; CORE_ONLY=1 lets the plain-JVM tests run anywhere.
if (System.getenv("CORE_ONLY") == null) include(":app")
