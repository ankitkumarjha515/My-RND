package com.myrnd.opencode.core

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class ProotCommandTest {
    private val config = ProotCommand.Config(
        proot = "/app/lib/libproot.so",
        loader = "/app/lib/libproot-loader.so",
        libraryDir = "/data/files/lib",
        tmpDir = "/data/files/tmp",
        rootfs = "/data/files/alpine",
        workdir = "/root/projects",
        binds = listOf(ProotCommand.Bind("/data/files/alpine/proc/.fake/stat", "/proc/stat")),
        env = mapOf("HOME" to "/root", "OPENCODE_PASSWORD" to "secret"),
    )

    @Test
    fun startsWithProotAndEndsWithGuestCommand() {
        val argv = ProotCommand.argv(config, listOf("/usr/local/bin/opencode", "serve"))
        assertEquals("/app/lib/libproot.so", argv.first())
        assertEquals(listOf("/usr/local/bin/opencode", "serve"), argv.takeLast(2))
    }

    @Test
    fun setsRootfsWorkdirAndRootIdentity() {
        val argv = ProotCommand.argv(config, listOf("/bin/true"))
        assertTrue(argv.contains("--rootfs=/data/files/alpine"))
        assertTrue(argv.contains("--cwd=/root/projects"))
        assertTrue(argv.contains("--root-id"))
        assertTrue(argv.contains("--kill-on-exit"))
        assertTrue(argv.contains("--link2symlink"))
    }

    @Test
    fun bindsSystemDirsSharedMemoryAndExtraBinds() {
        val argv = ProotCommand.argv(config, listOf("/bin/true"))
        assertTrue(argv.contains("--bind=/dev"))
        assertTrue(argv.contains("--bind=/proc"))
        assertTrue(argv.contains("--bind=/sys"))
        assertTrue(argv.contains("--bind=/data/files/alpine/tmp:/dev/shm"))
        assertTrue(argv.contains("--bind=/data/files/alpine/proc/.fake/stat:/proc/stat"))
    }

    @Test
    fun guestGetsOnlyTheGivenEnvironment() {
        val argv = ProotCommand.argv(config, listOf("/bin/true"))
        val envStart = argv.indexOf("/usr/bin/env")
        assertEquals("-i", argv[envStart + 1])
        assertEquals(listOf("HOME=/root", "OPENCODE_PASSWORD=secret"), argv.subList(envStart + 2, envStart + 4))
        assertEquals("/bin/true", argv[envStart + 4])
    }

    @Test
    fun hostEnvironmentPointsProotAtLoaderTmpAndLibraries() {
        val env = ProotCommand.hostEnv(config)
        assertEquals("/app/lib/libproot-loader.so", env["PROOT_LOADER"])
        assertEquals("/data/files/tmp", env["PROOT_TMP_DIR"])
        assertEquals("/data/files/lib", env["LD_LIBRARY_PATH"])
        assertFalse(env.containsKey("OPENCODE_PASSWORD"))
    }

    @Test
    fun fakeProcBindsOnlyForUnreadableEntries() {
        val readable = setOf("/proc/uptime", "/proc/version")
        val binds = ProotCommand.fakeProcBinds("/r/proc/.fake") { it in readable }
        assertEquals(
            listOf(
                ProotCommand.Bind("/r/proc/.fake/loadavg", "/proc/loadavg"),
                ProotCommand.Bind("/r/proc/.fake/stat", "/proc/stat"),
                ProotCommand.Bind("/r/proc/.fake/vmstat", "/proc/vmstat"),
            ),
            binds,
        )
    }

    @Test
    fun fakeProcContentExistsForEveryEntry() {
        ProotCommand.FAKE_PROC.keys.forEach { assertTrue(ProotCommand.FAKE_PROC.getValue(it).isNotBlank()) }
    }
}
