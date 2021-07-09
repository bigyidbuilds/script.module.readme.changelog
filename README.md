# script.gui.markdown.syntax.userguide

Converts a markdown syntax file in to a script gui that is viewable in Kodi

### Conversion Notes

1. Text containing HyperLinks are converted to a clickable button which will open with system web browser, If the text contains more then 1 hyperlink a dialog box will open asking which link you would like to open
2. Images which have a pixel size of less then 200x200 will be added as size, Images larger will converted to a thumbnail and then will be clickable and open in a full screen view

### Example mode

Script can run in a example type mode that uses a markdown example file in the script folder, to run this way locate the script in my addons in kodi and run 

### Method to call

`RunScript(script.gui.markdown.syntax.userguide,mdpath)`

`mdpath` is the path to the readme file

File can be called from a local file or a url 
 
using built in method `xbmc.executebuiltin('RunScript(script.gui.markdown.syntax.userguide,mdpath)')`

Refer to the reference guides for [basic syntax](https://www.markdownguide.org/basic-syntax) and [extended syntax](https://www.markdownguide.org/extended-syntax) use.

## Change Log

### Version 1.0.0

Initial Release