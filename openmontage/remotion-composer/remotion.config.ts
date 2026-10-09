import {Config} from '@remotion/cli/config';

// This sandbox routes outbound HTTPS through a proxy whose CA isn't in
// Chromium's trust store, so Google Fonts fetches fail with
// ERR_CERT_AUTHORITY_INVALID during render. Ignore cert errors so the
// zero-key demo can render here.
Config.setChromiumIgnoreCertificateErrors(true);
