
* This is a subset of  
github.com/hakimel/reveal.js/  - directory `dist`

* No need for node or any "installation" with npm.

* Simply include the CSS and JS modules.

* Example: ./templates/reveal-js-adapter.html

* Rendering the markdown from _another file_,  
  => requires running a webserver

* `custom.css` - additional layout styling

* `./theme/simple.css` - modified, to load font-family from local webserver - 
   not from google fonts

   * also the main font-family was changed from `Lato` to `News Cycle`

   ```css
    /* --r-main-font: Lato, sans-serif; */
    --r-main-font: News Cycle, Impact, sans-serif;

   ```
