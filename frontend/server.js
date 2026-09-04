// Minimal static file server for the Jacqueline Magawa portfolio.
// Serves the static site located at the repository root (parent of /frontend)
// on the port provided by the environment (3000 in this environment).
// Supports HTTP Range requests so <video> seeking / progressive playback works.
const http = require("http");
const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..");
const PORT = process.env.PORT || 3000;
const HOST = process.env.HOST || "0.0.0.0";

const HTTP_OK = 200;
const HTTP_PARTIAL_CONTENT = 206;
const HTTP_FORBIDDEN = 403;
const HTTP_NOT_FOUND = 404;
const HTTP_SERVER_ERROR = 500;
const HTTP_RANGE_NOT_SATISFIABLE = 416;

const CACHE_CONTROL = "public, max-age=3600";

const MIME = {
  ".html": "text/html; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".js": "application/javascript; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".gif": "image/gif",
  ".svg": "image/svg+xml",
  ".webp": "image/webp",
  ".ico": "image/x-icon",
  ".mp4": "video/mp4",
  ".webm": "video/webm",
  ".pdf": "application/pdf",
  ".woff": "font/woff",
  ".woff2": "font/woff2",
  ".ttf": "font/ttf",
};

function contentType(filePath) {
  const ext = path.extname(filePath).toLowerCase();
  return MIME[ext] || "application/octet-stream";
}

// Parse a Range header into a clamped { start, end } pair for the given size.
function parseRange(range, size) {
  const match = /bytes=(\d*)-(\d*)/.exec(range);
  let start = match && match[1] ? parseInt(match[1], 10) : 0;
  let end = match && match[2] ? parseInt(match[2], 10) : size - 1;
  if (isNaN(start) || start < 0) start = 0;
  if (isNaN(end) || end >= size) end = size - 1;
  return { start, end };
}

// Serve a partial (206) response for Range requests (video seeking).
function handleRangeRequest(req, res, filePath, stat, type) {
  const { start, end } = parseRange(req.headers.range, stat.size);
  if (start > end) {
    res.writeHead(HTTP_RANGE_NOT_SATISFIABLE, {
      "Content-Range": `bytes */${stat.size}`,
    });
    res.end();
    return;
  }
  res.writeHead(HTTP_PARTIAL_CONTENT, {
    "Content-Type": type,
    "Content-Range": `bytes ${start}-${end}/${stat.size}`,
    "Accept-Ranges": "bytes",
    "Content-Length": end - start + 1,
    "Cache-Control": CACHE_CONTROL,
  });
  fs.createReadStream(filePath, { start, end }).pipe(res);
}

// Serve a full (200) response.
function serveFile(res, filePath, stat, type) {
  res.writeHead(HTTP_OK, {
    "Content-Type": type,
    "Content-Length": stat.size,
    "Accept-Ranges": "bytes",
    "Cache-Control": CACHE_CONTROL,
  });
  fs.createReadStream(filePath).pipe(res);
}

function serve(req, res, filePath, stat) {
  const type = contentType(filePath);
  if (req.headers.range) {
    handleRangeRequest(req, res, filePath, stat, type);
    return;
  }
  serveFile(res, filePath, stat, type);
}

// Resolve the request URL to a safe path inside ROOT, or null if it escapes.
function resolvePath(reqUrl) {
  let urlPath = decodeURIComponent(reqUrl.split("?")[0]);
  if (urlPath === "/") urlPath = "/index.html";
  const resolved = path.normalize(path.join(ROOT, urlPath));
  return resolved.startsWith(ROOT) ? resolved : null;
}

// Fall back to index.html (SPA-style) when the requested file is missing.
function serveFallback(req, res) {
  const indexPath = path.join(ROOT, "index.html");
  fs.stat(indexPath, (err, stat) => {
    if (err) {
      res.writeHead(HTTP_NOT_FOUND);
      res.end("Not found");
      return;
    }
    serve(req, res, indexPath, stat);
  });
}

const server = http.createServer((req, res) => {
  try {
    const resolved = resolvePath(req.url);
    if (!resolved) {
      res.writeHead(HTTP_FORBIDDEN);
      res.end("Forbidden");
      return;
    }
    fs.stat(resolved, (err, stat) => {
      if (err || !stat.isFile()) {
        serveFallback(req, res);
        return;
      }
      serve(req, res, resolved, stat);
    });
  } catch (e) {
    res.writeHead(HTTP_SERVER_ERROR);
    res.end("Server error");
  }
});

server.listen(PORT, HOST);
