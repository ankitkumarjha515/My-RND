package com.myrnd.opencode.core

import org.apache.commons.compress.archivers.tar.TarArchiveInputStream
import org.apache.commons.compress.compressors.gzip.GzipCompressorInputStream
import java.io.File
import java.io.InputStream
import java.nio.file.Files
import java.nio.file.Paths

/** Unpacks the Alpine rootfs. Android apps may not create hard links, so those become copies. */
object TarExtractor {
    fun extractTarGz(input: InputStream, dest: File) {
        val root = dest.canonicalFile
        TarArchiveInputStream(GzipCompressorInputStream(input.buffered())).use { tar ->
            while (true) {
                val entry = tar.nextEntry ?: break
                val target = inside(root, entry.name)
                when {
                    entry.isDirectory -> target.mkdirs()
                    entry.isSymbolicLink -> {
                        target.parentFile.mkdirs()
                        Files.deleteIfExists(target.toPath())
                        Files.createSymbolicLink(target.toPath(), Paths.get(entry.linkName))
                    }
                    entry.isLink -> {
                        target.parentFile.mkdirs()
                        val source = inside(root, entry.linkName)
                        if (!source.isFile) throw IllegalStateException("Hard link ${entry.name} points to missing ${entry.linkName}")
                        source.copyTo(target, overwrite = true)
                        if (source.canExecute()) target.setExecutable(true, false)
                    }
                    entry.isFile -> {
                        target.parentFile.mkdirs()
                        Files.deleteIfExists(target.toPath())
                        target.outputStream().use { tar.copyTo(it) }
                        if (entry.mode and "111".toInt(8) != 0) target.setExecutable(true, false)
                    }
                    // Device nodes and FIFOs cannot be created by an app; proot binds the host's /dev instead.
                    else -> Unit
                }
            }
        }
    }

    // Lexical check: canonicalFile would follow absolute symlinks already in the rootfs out to host paths.
    // Parent directories must not be symlinks either, or writing "a/x" after "a -> /elsewhere" would escape.
    private fun inside(root: File, name: String): File {
        val target = root.toPath().resolve(name).normalize()
        if (!target.startsWith(root.toPath())) throw IllegalStateException("Archive entry escapes destination: $name")
        var parent = target.parent
        while (parent != null && parent != root.toPath()) {
            if (Files.isSymbolicLink(parent)) throw IllegalStateException("Archive entry goes through a symlink: $name")
            parent = parent.parent
        }
        return target.toFile()
    }
}
