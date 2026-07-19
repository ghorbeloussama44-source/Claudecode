const { handleUpload } = require('@vercel/blob/client');

// This route hands out short-lived tokens that let the browser upload a
// clip directly to Vercel Blob storage, bypassing this server entirely for
// the actual file bytes. That's required, not just an optimization: a
// Vercel Function's request body is capped at 4.5 MB, well under the size of
// almost any real video clip.
//
// NOTE: there is no user authentication in front of this endpoint (this is a
// public tool, no accounts). The only guardrails are the content-type and
// size restrictions below, plus the random-suffixed, unguessable blob path.
// If this deploys somewhere with real traffic, anyone can call this route to
// get an upload token, which is a storage-cost exposure worth knowing about.
module.exports = async function handler(request) {
  const body = await request.json();

  try {
    const jsonResponse = await handleUpload({
      body,
      request,
      onBeforeGenerateToken: async () => ({
        allowedContentTypes: ['video/*'],
        addRandomSuffix: true,
        maximumSizeInBytes: 500 * 1024 * 1024,
      }),
      onUploadCompleted: async () => {
        // No database to update — the client already has the blob URL from
        // the upload() call and sends it to /api/finalize itself.
      },
    });

    return Response.json(jsonResponse);
  } catch (error) {
    return Response.json({ error: error.message }, { status: 400 });
  }
};
