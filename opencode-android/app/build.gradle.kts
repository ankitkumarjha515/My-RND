plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "com.myrnd.opencode"
    compileSdk = 35

    defaultConfig {
        applicationId = "com.myrnd.opencode"
        minSdk = 26
        // Like Termux, target API 28 so the bundled Linux userland may execute files from app storage.
        targetSdk = 28
        versionCode = (System.getenv("GITHUB_RUN_NUMBER") ?: "1").toInt()
        versionName = "0.1.$versionCode"
        ndk { abiFilters += "arm64-v8a" }
    }

    buildTypes {
        // Not debuggable, so `adb run-as` cannot read the app's data. Signed with the CI's cached debug key
        // until a real release key is added.
        release {
            isMinifyEnabled = false
            signingConfig = signingConfigs.getByName("debug")
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    kotlinOptions {
        jvmTarget = "17"
    }

    packaging {
        jniLibs {
            // proot and its loader are executables shipped as .so files; they must be extracted to disk unmodified.
            useLegacyPackaging = true
            keepDebugSymbols += "**/*.so"
        }
    }

    lint {
        disable += "ExpiredTargetSdkVersion"
    }
}

dependencies {
    implementation(project(":core"))
}
