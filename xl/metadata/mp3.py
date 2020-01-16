# Copyright (C) 2008-2010 Adam Olsen
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
#
# The developers of the Exaile media player hereby grant permission
# for non-GPL compatible GStreamer and Exaile plugins to be used and
# distributed together with GStreamer and Exaile. This permission is
# above and beyond the permissions granted by the GPL license by which
# Exaile is covered. If you modify this code, you may extend this
# exception to your version of the code, but you are not obligated to
# do so. If you do not wish to do so, delete this exception statement
# from your version.
import copy

from xl.metadata._base import CoverImage, NotWritable
from xl.metadata._id3 import ID3Format
from eyed3.mp3 import Mp3AudioFile


class MP3Format(ID3Format):
    MutagenType = Mp3AudioFile

    def get_keys_disk(self):
        keys = []
        for v in self._get_raw().tag.frame_set \
                        if self._get_raw().tag else []:
            k = str(v, "ascii")
            if k in self._reverse_mapping:
                keys.append(self._reverse_mapping[k])
            else:
                keys.append(k)
        return keys

    def get_length(self):
        return self.mutagen.info.time_secs

    def get_bitrate(self):
        return self.mutagen.info.bit_rate[1]  # [0] is vbr boolean

    def _init_tag(self, raw):
        if raw.tag is None:
            raw.initTag()
            return True

    def _get_tag(self, raw, t):
        if not raw.tag:
            return []

        if t not in self.tag_mapping.values():
            t = "TXXX:" + t

        frames = raw.tag.frame_set[t.encode("latin1")]
        if len(frames) <= 0:
            return []

        ret = []
        if t in ('TDRC', 'TDOR'):  # values are ID3TimeStamps, need str conversion
            ret.append(str(raw.tag.original_release_date
                           if t == "TDOR" else str(raw.tag.recording_date)))
        elif t == 'USLT':  # Lyrics are stored in a single str object
            # XXX: Ideally exaile language setting would be used to get a matching lyrics frame
            for lyrics in raw.tag.lyrics:
                ret.append(lyrics.text)
        elif (
            t == 'WOAR'
        ):  # URLs are stored in url field instead of text field (as a single str object)
            ret.append(frames[0].url.replace('\n', '').replace('\r', ''))
        elif t == 'APIC':
            ret = [
                CoverImage(type=f.picture_type, desc=f.description, mime=f.mime_type,
                           data=f.image_data)
                for f in raw.tag.images
            ]
        elif t == 'COMM':  # Newlines within comments are allowed, keep them
            for comment in raw.tag.comments:
                ret.append(comment.text)
        else:
            for value in frames:
                ret.append(value.text)

        return ret

    def _set_tag(self, raw, tag, data):

        print("tag:", tag)
        if tag not in self.tag_mapping.values():
            tag = "TXXX:" + tag

        if raw.tag is not None:
            raw.tags.delall(tag)

        # FIXME: Properly set and retrieve multiple values
        if tag == 'USLT':
            data = data[0]

        if tag == 'APIC':
            frames = [
                id3.Frames[tag](
                    encoding=3,
                    mime=info.mime,
                    type=info.type,
                    desc=info.desc,
                    data=info.data,
                )
                for info in data
            ]
        elif tag == 'COMM':
            frames = [
                id3.COMM(encoding=3, text=d, desc='', lang='\x00\x00\x00') for d in data
            ]
        elif tag == 'WOAR':
            frames = [id3.WOAR(encoding=3, url=d) for d in data]
        else:
            frames = [id3.Frames[tag](encoding=3, text=data)]

        if raw.tags is not None:
            for frame in frames:
                raw.tags.add(frame)

    def _del_tag(self, raw, tag):
        if tag not in self.tag_mapping.values():
            tag = "TXXX:" + tag
        if raw.tags is not None:
            raw.tags.delall(tag)

# vim: et sts=4 sw=4
