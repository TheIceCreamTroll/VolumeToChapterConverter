# Volume-to-Chapter Converter

To split a Comic / Manga volume into its chapters, run `python ExtractChaptersFromVolume.py`. If you are on Linux, 
you may need to replace `python` with `python3`

For the extraction to work, the filenames of your volume's images should look something like: 
> Series Title - c001 (v01) - p000 [optional chapter title] [some other stuff that doesn't matter].png

> Series Title - 001x2 [optional chapter title] [some other stuff that doesn't matter].png

> Series Title - 001 (v01) - p000  [some other stuff that doesn't matter] [optional chapter title].png

What's important is the `c001 (v01)` pattern. As long as the filenames follow it, or another commonly used format, 
your files should parse just fine

### Parsing Chapter Titles
If the chapter title is part of an image's filename, and you want it added to the filename of the chapter, use the
`p` / `--parse` argument to enable parsing, and pass the chapter title's index (which starts at 0) with `-i` / `--index`

Only the first file of each chapter will have its title parsed

Examples:
* `Series Title - c001 (v01) - p000 [Chapter Title] [sometingelse].jpg` To get the chapter title, use `-i 0`
* `Series Title - c002 (v01) - p000 [sometingelse] [Chapter Title].jpg` To get the chapter title, use `-i 1`

A negative index can also be used when there are an inconsistent amount of bracketed text to the left of the title:
* `Series Title - c001 (v01) - p000 [sometingelse] [Chapter Title].jpg` 
* `Series Title - c002 (v01) - p000 [sometingelse] [sometingextra] [Chapter Title].jpg` To get the chapter title for both, use `-i -1`

### Adding metadata to your new chapters
To bulk-add metadata to your chapters, I highly recommend [ThePromidius](https://github.com/ThePromidius)'s [Manga-Manager](https://github.com/ThePromidius/Manga-Manager) and / or my [BatchComicTagger](https://github.com/TheIceCreamTroll/BatchComicTagger), which can also scrape metadata from some Fandom wikis
