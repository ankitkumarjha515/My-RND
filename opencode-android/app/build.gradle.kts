import java.util.Properties

plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

val appVersion = Properties().apply { rootProject.file("version.properties").inputStream().use { load(it) } }
    .getProperty("appVersion") ?: error("appVersion missing from version.properties")
val openCodeVersion = Regex("^version=(\\S+)$", RegexOption.MULTILINE)
    .find(file("src/main/assets/setup.sh").readText())?.groupValues?.get(1)
    ?: error("OpenCode version pin missing from setup.sh")

android {
    namespace = "com.myrnd.opencode"
    compileSdk = 35

    defaultConfig {
        applicationId = "com.myrnd.opencode"
        minSdk = 26
        // Like Termux, target API 28 so the bundled Linux userland may execute files from app storage.
        targetSdk = 28
        // The build number only ever grows, so every CI build installs over the last one.
        versionCode = (System.getenv("GITHUB_RUN_NUMBER") ?: "1").toInt()
        versionName = "$appVersion (OpenCode $openCodeVersion)"
        buildConfigField("String", "APP_VERSION", "\"$appVersion\"")
        buildConfigField("String", "OPENCODE_VERSION", "\"$openCodeVersion\"")
        ndk { abiFilters += "arm64-v8a" }
    }

    buildFeatures {
        buildConfig = true
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
