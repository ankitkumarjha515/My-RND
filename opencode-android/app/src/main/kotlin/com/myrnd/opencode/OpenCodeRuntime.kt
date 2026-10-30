package com.myrnd.opencode

import android.Manifest
import android.content.Context
import android.content.pm.PackageManager
import android.os.Build
import android.os.Environment
import com.myrnd.opencode.core.ProotCommand
import com.myrnd.opencode.core.TarExtractor
import java.io.File
import java.nio.file.Files
import java.security.SecureRandom
import java.util.Base64

/** Owns the on-device Linux: unpacking Alpine, first-run setup, and launching commands inside it through proot. */
class OpenCodeRuntime(private val context: Context) {
    companion object {
        const val PORT = 4096
        const val BASE_URL = "http://127.0.0.1:$PORT"
        private const val OPENCODE = "/usr/local/bin/opencode"
        private const val SETUP_SCRIPT = "/.opencode/setup.sh"
        private const val STORAGE = "/storage/emulated/0"
    }

    private val files = context.filesDir
    private val nativeDir = File(context.applicationInfo.nativeLibraryDir)
    private val rootfs = File(files, "alpine")
    private val tmp = File(files, "tmp")
    private val lib = File(files, "lib")
    private val state = File(rootfs, ".opencode")
    private val rootfsReady = File(state, "rootfs-ready")
    private val setupDone = File(state, "setup-done")
    val serverLog = File(files, "server.log")

    val password: String by lazy {
        val prefs = context.getSharedPreferences("opencode", Context.MODE_PRIVATE)
        prefs.getString("server_password", null) ?: ByteArray(32).also { SecureRandom().nextBytes(it) }
            .let { Base64.getUrlEncoder().withoutPadding().encodeToString(it) }
            .also { prefs.edit().putString("server_password", it).apply() }
    }

    fun isSetUp() = setupDone.exists()

    fun resetSetup() {
        setupDone.delete()
    }

    fun hasStorageAccess() =
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) Environment.isExternalStorageManager()
        else context.checkSelfPermission(Manifest.permission.WRITE_EXTERNAL_STORAGE) == PackageManager.PERMISSION_GRANTED

    /** Unpacks Alpine (once) and installs git, ripgrep, bash and OpenCode inside it. Needs internet. */
    fun setUp(log: (String) -> Unit) {
        prepareHost()
        if (!rootfsReady.exists()) {
            log("Unpacking Linux…")
            rootfs.deleteRecursively()
            rootfs.mkdirs()
            context.assets.open("alpine-rootfs.tar.gz").use { TarExtractor.extractTarGz(it, rootfs) }
            state.mkdirs()
            rootfsReady.createNewFile()
        }
        prepareGuest()
        context.assets.open("setup.sh").use { input -> File(rootfs, SETUP_SCRIPT).outputStream().use { input.copyTo(it) } }
        val process = process(listOf("/bin/sh", SETUP_SCRIPT)).redirectErrorStream(true).start()
        process.inputStream.bufferedReader().forEachLine(log)
        val code = process.waitFor()
        if (code != 0) throw IllegalStateException("Setup failed (exit code $code). Check your internet connection and tap Retry.")
        setupDone.createNewFile()
    }

    /** Starts `opencode serve` on loopback; its output goes to [serverLog]. */
    fun startServer(): Process {
        prepareHost()
        prepareGuest()
        return process(
            listOf(OPENCODE, "serve", "--hostname", "127.0.0.1", "--port", PORT.toString()),
            mapOf("OPENCODE_PASSWORD" to password),
        ).redirectErrorStream(true).redirectOutput(serverLog).start()
    }

    fun serverLogTail(lines: Int = 40) =
        if (serverLog.exists()) serverLog.readLines().takeLast(lines).joinToString("\n") else ""

    private fun prepareHost() {
        val proot = File(nativeDir, "libproot.so")
        if (!proot.exists()) throw IllegalStateException("This APK was built without proot. Rebuild it with scripts/fetch-native.sh.")
        tmp.mkdirs()
        lib.mkdirs()
        // proot is linked against libtalloc.so.2; the APK can only ship it as libtalloc.so, and its directory moves on updates.
        val talloc = File(lib, "libtalloc.so.2").toPath()
        Files.deleteIfExists(talloc)
        Files.createSymbolicLink(talloc, File(nativeDir, "libtalloc.so").toPath())
    }

    private fun prepareGuest() {
        state.mkdirs()
        File(rootfs, "tmp").mkdirs()
        File(rootfs, "root/projects").mkdirs()
        // Android has no /etc/resolv.conf for Linux programs to read.
        File(rootfs, "etc/resolv.conf").writeText("nameserver 8.8.8.8\nnameserver 1.1.1.1\n")
        val fakeProc = File(state, "proc").apply { mkdirs() }
        ProotCommand.FAKE_PROC.forEach { (name, content) -> File(fakeProc, name).writeText(content) }
    }

    private fun process(command: List<String>, extraEnv: Map<String, String> = emptyMap()): ProcessBuilder {
        val fakeProcBinds = ProotCommand.fakeProcBinds(File(state, "proc").path) { runCatching { File(it).readText() }.isSuccess }
        val storageBinds = if (hasStorageAccess()) listOf(ProotCommand.Bind(STORAGE, "/sdcard")) else emptyList()
        val config = ProotCommand.Config(
            proot = File(nativeDir, "libproot.so").path,
            loader = File(nativeDir, "libproot-loader.so").path,
            libraryDir = lib.path,
            tmpDir = tmp.path,
            rootfs = rootfs.path,
            workdir = "/root/projects",
            binds = fakeProcBinds + storageBinds,
            env = mapOf(
                "HOME" to "/root",
                "USER" to "root",
                "PATH" to "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
                "SHELL" to "/bin/bash",
                "TERM" to "xterm-256color",
                "LANG" to "C.UTF-8",
                "TMPDIR" to "/tmp",
            ) + extraEnv,
        )
        return ProcessBuilder(ProotCommand.argv(config, command)).directory(files).also {
            it.environment().clear()
            it.environment().putAll(ProotCommand.hostEnv(config))
        }
    }
}
