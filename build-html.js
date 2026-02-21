const fs = require("fs");
const path = require("path");
const cheerio = require("cheerio");
const { minify } = require("html-minifier-terser");
const { execSync } = require("child_process");

const DIST = "compiled";
const HTML_SRC = "assets/index.html";
const CSS_SRC = "assets/css";
const IMG_SRC = "assets/img";

async function build() {
  // Ensure folder
  if (!fs.existsSync(DIST)) fs.mkdirSync(DIST, { recursive: true });

  // Copy Images (preserve folder structure relative to assets)
  const copyRecursive = (srcDir, destDir) => {
    if (!fs.existsSync(srcDir)) return;
    const entries = fs.readdirSync(srcDir, { withFileTypes: true });
    entries.forEach(entry => {
      const srcPath = path.join(srcDir, entry.name);
      const destPath = path.join(destDir, path.relative('assets', srcPath));

      // SKIP json folder inside compiled
      if (destPath.startsWith(path.join(DIST, 'json'))) return;

      if (entry.isDirectory()) {
        fs.mkdirSync(destPath, { recursive: true });
        copyRecursive(srcPath, destDir);
      } else {
        fs.mkdirSync(path.dirname(destPath), { recursive: true });
        fs.copyFileSync(srcPath, destPath);
      }
    });
  };

  copyRecursive(IMG_SRC, DIST);

  // Load HTML
  let html = fs.readFileSync(HTML_SRC, "utf-8");
  const $ = cheerio.load(html);

  // INLINE CSS
  $('link[rel="stylesheet"]').each((i, el) => {
    const href = $(el).attr('href');
    if (href.startsWith('css/')) {
      const cssPath = path.join(CSS_SRC, path.basename(href));
      if (fs.existsSync(cssPath)) {
        const cssContent = fs.readFileSync(cssPath, "utf-8");
        // Insert <style> with CSS before this <link>
        $(el).before(`<style>${cssContent}</style>`);
      }
      // Remove the original <link>
      $(el).remove();
    }
  });

  // Remove all old script tags
  $('script').remove();

  // Add bundle script at end of body
  $('body').append('<script src="bundle.min.js" defer></script>');

  // Minify HTML
  const minified = await minify($.html(), {
    collapseWhitespace: true,
    removeComments: true,
    minifyCSS: true,
    minifyJS: true,
  });

  // Write file
  fs.writeFileSync(path.join(DIST, "index.html"), minified);

  console.log("HTML updated, CSS inlined, bundle added, images copied (JSON preserved)!");
}

build().catch(err => {
  console.error(err);
  process.exit(1);
});