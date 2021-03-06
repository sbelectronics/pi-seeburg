import csv
import os

src_pdf = None
cur_pdf = None
song_count = 0
pdf_count = 0
song_table = {}

TITLES_PER_PAGE=32

def output_pdf():
    global cur_pdf, pdf_count

    dest_pdf = open("rtstrips_data_%d.fdf" % pdf_count, "wb")
    dest_pdf.write(cur_pdf)

    dest_pdf.close()

    os.system("pdftk rtstrips.pdf fill_form rtstrips_data_%d.fdf output rtstrips_%d.pdf" % (pdf_count, pdf_count))

    pdf_count += 1
    cur_pdf = src_pdf

def safe_replace(s, old, new):
    x = s.find(old, 0)
    if x<0:
        raise Exception("failed to find %s" % old)
    x = s.find(old, x+1)
    if x>0:
        raise Exception("multiple matches for %s" % old)

    return s.replace(old, new)

def add_title(artist, song):
    global song_count, cur_pdf

    if ((song_count % TITLES_PER_PAGE) == 0) and (song_count > 0):
        output_pdf()

    page_song_count = song_count % TITLES_PER_PAGE

    strip = (page_song_count/2) + 1
    pos =  page_song_count % 2

    print "XXX", song_count, strip, pos, artist, song, pdf_count

    if (pos == 0):
        cur_pdf = safe_replace(cur_pdf, "(A%d)" % strip, "(%s)" % artist)
        cur_pdf = safe_replace(cur_pdf, "(\"S%da\")" % strip, "(\"%s\")" % song)
    else:
        cur_pdf = safe_replace(cur_pdf, "(\"S%db\")" % strip, "(\"%s\")" % song)

    song_count = song_count + 1

def output_song_table():
    f = file("song_table.py","wt")
    f.write("song_table = {\n")

    for (k,v) in song_table.items():
        f.write('     "%s": {"filename": "%s", "artist": "%s", "song": "%s"},\n' % (k, v["filename"], v["artist"], v["song"]))

    f.write("}\n")

def main():
    global src_pdf, cur_pdf, song_table

    src_pdf = open("rtstrips_data.fdf", "rb").read()
    cur_pdf = src_pdf

    f = open("songs.csv", "rt")
    reader = csv.reader(f)
    for row in reader:
        (number, letter, artist, song, filename) = row # line.strip().split(",",4)
        number = number.strip()
        letter = letter.strip()
        artist = artist.strip()
        song = song.strip()
        filename = filename.strip()

        if (number=="Number"):
            # header at the top of the page
            continue

        if (letter and artist and song and filename):
            add_title(artist, song)

            select = "%s%s" % (letter, number)
            song_table[select] = {"filename": filename, "artist": artist, "song": song}

    output_pdf()

    output_song_table()
      
if __name__ == "__main__":
    main()
