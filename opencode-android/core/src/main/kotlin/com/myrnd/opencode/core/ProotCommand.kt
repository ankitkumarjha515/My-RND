package com.myrnd.opencode.core

/** Builds the proot invocation that runs a command inside the bundled Alpine rootfs. */
object ProotCommand {
    data class Bind(val host: String, val guest: String)

    data class Config(
        val proot: String,
        val loader: String,
        val libraryDir: String,
        val tmpDir: String,
        val rootfs: String,
        val workdir: String,
        val binds: List<Bind>,
        val env: Map<String, String>,
    )

    // Android's SELinux policy hides these from apps; programs that read them get a static stand-in instead.
    val FAKE_PROC = linkedMapOf(
        "loadavg" to "0.12 0.07 0.02 2/165 765\n",
        "stat" to "cpu  1957 0 2877 93280 262 342 254 87 0 0\ncpu0 31 0 226 12027 82 10 4 9 0 0\n" +
            "intr 63361 0 0 0 0 0 0 0 0 0 0 0 0 0\nctxt 38014093\nbtime 1694292441\nprocesses 26442\n" +
            "procs_running 1\nprocs_blocked 0\nsoftirq 75663 0 5903 6 25375 10774 0 243 11685 0 21677\n",
        "uptime" to "124.08 932.80\n",
        "version" to "Linux version 6.2.1 (proot@termux) (gcc (GCC) 12.2.1, GNU ld (GNU Binutils) 2.40) #1 SMP PREEMPT_DYNAMIC\n",
        "vmstat" to "nr_free_pages 1743136\nnr_zone_inactive_anon 179281\nnr_zone_active_anon 7183\n" +
            "nr_zone_inactive_file 22858\nnr_zone_active_file 51328\nnr_mlock 0\npgpgin 198\npgpgout 0\n",
    )

    fun fakeProcBinds(fakeDir: String, readable: (String) -> Boolean) =
        FAKE_PROC.keys.map { Bind("$fakeDir/$it", "/proc/$it") }.filterNot { readable(it.guest) }

    fun argv(config: Config, command: List<String>) =
        listOf(
            config.proot,
            "--kill-on-exit",
            "--link2symlink",
            "--sysvipc",
            "-L",
            "--root-id",
            "--rootfs=${config.rootfs}",
            "--cwd=${config.workdir}",
            "--bind=/dev",
            "--bind=/dev/urandom:/dev/random",
            "--bind=/proc",
            "--bind=/proc/self/fd:/dev/fd",
            "--bind=/sys",
            "--bind=${config.rootfs}/tmp:/dev/shm",
        ) + config.binds.map { "--bind=${it.host}:${it.guest}" } +
            listOf("/usr/bin/env", "-i") + config.env.map { "${it.key}=${it.value}" } + command

    fun hostEnv(config: Config) =
        mapOf(
            "PROOT_LOADER" to config.loader,
            "PROOT_TMP_DIR" to config.tmpDir,
            "LD_LIBRARY_PATH" to config.libraryDir,
        )
}
