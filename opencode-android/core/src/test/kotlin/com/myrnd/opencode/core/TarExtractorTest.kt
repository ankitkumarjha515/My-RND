package com.myrnd.opencode.core

import org.apache.commons.compress.archivers.tar.TarArchiveEntry
import org.apache.commons.compress.archivers.tar.TarArchiveOutputStream
import org.apache.commons.compress.archivers.tar.TarConstants
import org.apache.commons.compress.compressors.gzip.GzipCompressorOutputStream
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertThrows
import org.junit.Assert.assertTrue
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder
import java.io.ByteArrayInputStream
import java.io.ByteArrayOutputStream
import java.nio.file.Files

class TarExtractorTest {
    @get:Rule
    val tmp = TemporaryFolder()

    private fun archive(build: TarArchiveOutputStream.() -> Unit): ByteArrayInputStream {
        val bytes = ByteArrayOutputStream()
        TarArchiveOutputStream(GzipCompressorOutputStream(bytes)).use { it.build() }
        return ByteArrayInputStream(bytes.toByteArray())
    }

    private fun TarArchiveOutputStream.file(name: String, content: String, mode: Int = "644".toInt(8)) {
        val data = content.toByteArray()
        putArchiveEntry(TarArchiveEntry(name).apply { size = data.size.toLong(); this.mode = mode })
        write(data)
        closeArchiveEntry()
    }

    private fun TarArchiveOutputStream.link(name: String, target: String, type: Byte) {
        putArchiveEntry(TarArchiveEntry(name, type).apply { linkName = target })
        closeArchiveEntry()
    }

    @Test
    fun extractsDirectoriesFilesAndExecutableBit() {
        val dest = tmp.newFolder("root")
        val input = archive {
            putArchiveEntry(TarArchiveEntry("bin/")); closeArchiveEntry()
            file("bin/busybox", "binary", "755".toInt(8))
            file("etc/motd", "hello")
        }
        TarExtractor.extractTarGz(input, dest)
        assertEquals("hello", dest.resolve("etc/motd").readText())
        assertTrue(dest.resolve("bin/busybox").canExecute())
        assertFalse(dest.resolve("etc/motd").canExecute())
    }

    @Test
    fun keepsSymlinksAsGivenEvenWhenAbsolute() {
        val dest = tmp.newFolder("root")
        val input = archive {
            file("bin/busybox", "binary", "755".toInt(8))
            link("bin/sh", "/bin/busybox", TarConstants.LF_SYMLINK)
        }
        TarExtractor.extractTarGz(input, dest)
        val link = dest.resolve("bin/sh").toPath()
        assertTrue(Files.isSymbolicLink(link))
        assertEquals("/bin/busybox", Files.readSymbolicLink(link).toString())
    }

    @Test
    fun replacesAnEntryThatIsAlreadyAnAbsoluteSymlink() {
        val dest = tmp.newFolder("root")
        // An absolute link target that exists on the host, as /system paths do on a phone.
        val outside = tmp.newFile("host-busybox").absolutePath
        val input = archive {
            link("bin/sh", outside, TarConstants.LF_SYMLINK)
            link("bin/sh", "/bin/bash", TarConstants.LF_SYMLINK)
        }
        TarExtractor.extractTarGz(input, dest)
        assertEquals("/bin/bash", Files.readSymbolicLink(dest.resolve("bin/sh").toPath()).toString())
    }

    @Test
    fun turnsHardLinksIntoCopies() {
        val dest = tmp.newFolder("root")
        val input = archive {
            file("usr/bin/a", "same", "755".toInt(8))
            link("usr/bin/b", "usr/bin/a", TarConstants.LF_LINK)
        }
        TarExtractor.extractTarGz(input, dest)
        assertEquals("same", dest.resolve("usr/bin/b").readText())
        assertTrue(dest.resolve("usr/bin/b").canExecute())
    }

    @Test
    fun rejectsEntriesThatEscapeTheDestination() {
        val dest = tmp.newFolder("root")
        val input = archive { file("../evil", "x") }
        assertThrows(IllegalStateException::class.java) { TarExtractor.extractTarGz(input, dest) }
        assertFalse(dest.parentFile.resolve("evil").exists())
    }
}
