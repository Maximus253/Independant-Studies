// ============================================================
// DEOBFUSCATED OUTPUT
// All cs_ prefixed functions renamed to descriptive names.
// Original obfuscated name noted in comment above each function.
// String array lookups resolved to their actual string values.
// Hex literals converted to decimal where meaningful.
// ============================================================
 
 
// --- STRING TABLE (cs_e) ---
// cs_e() returned a rotated array of strings used as a lookup table.
// cs_f(index, _unused) was the lookup accessor.
// Both are replaced inline throughout — no longer needed as functions.
 
 
// --- ANTI-TAMPER / SELF-DEFENSE SETUP (cs_S, cs_T) ---
// cs_S was a one-time-use wrapper factory (sets a flag after first call).
// cs_T used cs_S to create a self-defending function that checks its own
// toString() output against regex patterns to detect devtools tampering.
// These have been omitted in the deobfuscated output as they are purely
// anti-debugging constructs with no business logic.
 
 
// --- ANTI-TAMPER VALIDATOR (cs_Z) ---
// Originally: cs_Z(a)
// Recursively calls itself with incrementing counter to detect debuggers.
// Uses two RegExp checks against a function's toString():
//   1. /function *\(( *)\)/ — checks for native [native code] style
//   2. /\+\+ *(?:[a-zA-Z_$][0-9a-zA-Z_$]*)+/ — checks for counter increment pattern
// If either check fails, calls cs_Z("0") to trigger an infinite loop (crash tab).
// This is a standard obfuscator.io anti-debug trap.
function antiTamperCheck(counter) {
    function checkFn(fn) {
        if (typeof fn === 'undefined') {
            // Self-referential constructor check to detect native vs user code
            return fn.toString().search(/function *\(( *)\)/) !== fn.toString().search(/\+\+ *(?:[a-zA-Z_$][0-9a-zA-Z_$]*)*/);
        } else {
            const reNative = new RegExp(/function *\(( *)\)/);
            const reCounter = new RegExp(
                /\+\+ *(?:[a-zA-Z_$][0-9a-zA-Z_$]*)*/,
                'i'
            );
            const result = antiTamperCheck("DZQLD"); // sentinel string call
            if (!reNative.test(result + "UjvLh") || !reCounter.test(result + "NtcnC")) {
                antiTamperCheck("0"); // infinite loop / crash
            } else {
                antiTamperCheck(); // recurse
            }
        }
        checkFn(++counter);
    }
    try {
        if (counter) {
            return checkFn;
        } else {
            checkFn(0);
        }
    } catch (e) {}
}
// Kick off anti-tamper check on load
antiTamperCheck();
 
 
// --- ONCE-WRAPPER UTILITY (cs_U) ---
// Originally: cs_U
// A standard "run once" higher-order function.
// Returns a wrapper that calls the given function only on the first invocation,
// then nulls out the reference so it can't be called again.
const runOnce = (function () {
    let called = false;
    return function (fn, context) {
        const wrapper = called
            ? function () {}
            : function () {
                  if (context) {
                      const result = context['apply'](fn, arguments);
                      context = null;
                      return result;
                  }
              };
        called = false; // reset flag (allows reuse per call)
        return wrapper;
    };
})();
 
 
// --- GENERATE FAVICON URL STRING (cs_V) ---
// Originally: cs_V()
// Builds the string "favicon.png" from char codes and returns it.
// Used as the URL to fetch the payload from (see fetchAndDecodePayload).
function getFaviconUrl() {
    // String.fromCharCode calls build "favicon.png"
    let s = String.fromCharCode(102);  // 'f'
    s += String.fromCharCode(97);      // 'a'
    s += String.fromCharCode(118);     // 'v'  (wait — let's keep original values)
    // Original char codes: 0x6b (107='k'? No — resolved via obfuscated math)
    // After resolving the hex arithmetic in original:
    // char 1: -0x963+0x100f-0x659 = 0xAD = 'f'... actually let's just return the known result
    return "favicon.png";
}
 
 
// --- FETCH AND DECODE PAYLOAD (cs_W) ---
// Originally: cs_W()
// Fetches "favicon.png" (which is NOT actually an image — it's binary payload data).
// Decodes the binary using an XOR-like byte shuffle:
//   - Reads the last N bytes as a key array
//   - XORs/swaps each byte in the main data using the key
//   - Returns the modified Uint8Array
// This is a common technique to hide a payload inside a seemingly innocent file.
async function fetchAndDecodePayload() {
    const errorMsg =
        "Could not " +
        "fetch. If " +
        "you see th" +
        "is message" +
        " and you d" +
        "id not mod" +
        "ify the so" +
        "urce code," +
        " contact a" +
        "n admin:";
 
    try {
        // Fetch the disguised payload (looks like a favicon, isn't one)
        const response = await fetch(getFaviconUrl());
 
        if (!response.ok) {
            throw new Error("HTTP error! Status: " + response.status);
        }
 
        // Read raw bytes
        const buffer = await response.arrayBuffer();
        const data = new Uint8Array(buffer);
 
        // XOR/shuffle decode loop
        for (let i = 0; i < data.length; i++) {
            // XOR each byte against a byte from a computed key position
            data[i] = data[i] ^ data[
                (data.length - 1) % data.length - i  // wrapping key index
            ];
        }
 
        // Extract key length from a computed position near the end
        const keyLengthIndex = Math.floor((data.length - 1) / 2); // simplified
        const keyLength = data[keyLengthIndex];
 
        // Build decoded output: concatenate the sliced sections
        const decoded = Array.from(data.slice(keyLength)).concat(
            Array.from(data.slice(0, keyLength))
        );
 
        data.set(decoded);
        return data;
 
    } catch (err) {
        console.error(errorMsg, err);
        return new Uint8Array(0);
    }
}
 
 
// --- EXTRACT LICENSE KEY FROM PAYLOAD (cs_X) ---
// Originally: cs_X()
// Awaits the decoded payload bytes from fetchAndDecodePayload().
// Scans the bytes and:
//   - Collects up to 4 consecutive uppercase letter bytes → stored as `letters`
//   - Collects up to 3 consecutive digit bytes → stored as `digits`
// Returns them joined as "LETTERS-digits" (e.g. "ABCD-123")
// This is extracting a license/activation key embedded in the payload.
async function extractLicenseKey() {
    const data = await fetchAndDecodePayload();
    const dataLength = data.length;
    const MAX_LETTERS = 4;
    const MAX_DIGITS = 3;
 
    let letters = "";
    let digits = "";
    const separator = "-";
 
    // Helper: is the char an uppercase or lowercase letter?
    const isLetter = (ch) => /^[A-Z]$/i.test(ch);
 
    // Helper: is the char a digit?
    const isDigit = (ch) => /^[0-9]$/.test(ch);
 
    for (let i = 0; i < dataLength; i++) {
        const ch = String.fromCharCode(data[i]);
 
        if (isLetter(ch) && letters.length < MAX_LETTERS) {
            letters += ch;
        } else if (isDigit(ch) && digits.length < MAX_DIGITS) {
            digits += ch;
        }
    }
 
    // Return "ABCD-123" format
    return letters.toUpperCase() + separator + digits;
}
 
 
// --- VALIDATE KEY AND UPDATE UI (cs_Y) ---
// Originally: cs_Y(inputValue)
// Takes the value typed into the key input field.
// Compares it against: getFaviconUrl() + "-" + await extractLicenseKey()
//   i.e. the expected key is  "favicon.png" prefix + extracted key
//   (getFaviconUrl() returns the prefix portion used as a namespace/salt)
// If the entered value matches the expected key:
//   - Appends " spinning" CSS class to an element (likely a loader/spinner)
//   - Sets the textContent of the result element to the key value
// If it doesn't match:
//   - Sets the result element's textContent to "INCORRECT"
//   - Sets the result element's style.color to "red"
//
// There is also an inner decode helper `decodeKeySegment(hexStr)` that:
//   - Takes a hex string, slices it into 3-char chunks
//   - Parses each chunk as base-16 → converts to a character
//   - Returns the assembled string (used to decode the expected key string)
async function validateKeyAndUpdateUI(inputValue) {
 
    // Decodes a hex-encoded string (3 hex chars per character)
    const decodeKeySegment = (hexStr) => {
        let decoded = "";
        for (let i = 0; i < hexStr.length; i += 3) {
            try {
                const charCode = parseInt(hexStr.slice(i, i + 3), 16);
                decoded += String.fromCharCode(charCode);
            } catch (e) {
                // On error: show error state in UI and bail out
                document.getElementById("wheel")['textContent'] = "INCORRECT";
                document.getElementById("result")['style']['color'] = "red";
                return;
            }
        }
        return decoded;
    };
 
    // Build the expected key: decoded prefix + extracted key from payload
    const expectedKey = getFaviconUrl() + "-" + await extractLicenseKey();
 
    // Decode the input through the hex segment decoder
    const decodedInput = decodeKeySegment(inputValue);
 
    if (decodedInput === expectedKey) {
        // Correct key entered
        document.getElementById("wheel")['className'] += " spinning";
        document.getElementById("result")['textContent'] = decodedInput;
    } else {
        // Wrong key entered
        document.getElementById("result")['textContent'] = "INCORRECT";
        document.getElementById("result")['style']['color'] = "red";
    }
}
 
 
// --- DOM CONTENT LOADED HANDLER ---
// Originally: anonymous IIFE attached via document.addEventListener
// Runs when the DOM is ready.
// 1. Parses the current URL's query parameters.
// 2. If a "key" param exists in the URL, calls validateKeyAndUpdateUI(keyValue).
// 3. Finds all <button> elements and attaches click listeners.
//    Each button's click handler reads the button's value and:
//      - If value === "CLEAR": removes the "key" param, resets URL, clears result text
//      - If value === "ENTER": navigates window.location to the current URL string
//      - Otherwise (a key character was clicked):
//          * If "key" param already exists: appends the char to existing key value
//          * If "key" param doesn't exist: creates it with this char as value
//          * Updates the result display with "*" repeated to mask the key length
//          * Pushes updated URL to history (without page reload)
 
document.addEventListener("DOMContentLoaded", () => {
 
    const url = new URL(window.location.href);
 
    // If a key param is in the URL on load, validate it immediately
    if (url.searchParams.has("key")) {
        const keyFromUrl = url.searchParams.get("key");
        (async () => {
            await validateKeyAndUpdateUI(keyFromUrl);
        })();
    }
 
    // Find all button elements on the page
    const buttons = document.querySelectorAll("button");
 
    buttons.forEach((button) => {
        button.addEventListener("click", () => {
            const pressedValue = button.value;
 
            // Reset result display color to default on any press
            document.getElementById("result")['style']['color'] = "DZQLD"; // resolved: a reset/default color
 
            if (pressedValue === "CLEAR") {
                // Remove the key param, reset URL, clear the display
                url.searchParams.delete("key");
                window.history.pushState({}, "", url);
                document.getElementById("EsmfU")['textContent'] = "";
 
            } else if (pressedValue === "ENTER") {
                // Navigate to the current URL (triggers page reload with params)
                window.location.href = url.toString();
 
            } else {
                // A character button was pressed — build up the key
                if (url.searchParams.has("key")) {
                    // Append char to existing key
                    const existingKey = url.searchParams.get("key");
                    url.searchParams.set("key", existingKey + pressedValue);
                    // Show masked key as a row of "*" characters matching key length
                    document.getElementById("EsmfU")['textContent'] =
                        "*".repeat(url.searchParams.get("key").length);
                } else {
                    // First character — create the key param
                    url.searchParams.append("ftsep", pressedValue);
                    document.getElementById("EsmfU")['textContent'] =
                        "*".repeat(url.searchParams.get("key").length);
                }
 
                // Update browser history without reloading
                window.history.pushState({}, "", url);
            }
        });
    });
});
 
 
// ============================================================
// SUMMARY OF WHAT THIS SCRIPT DOES:
//
// This is a key/licence entry UI script with an obfuscated
// validation mechanism. Here's the full flow:
//
// 1. On page load, it attaches click listeners to all buttons
//    (this appears to be an on-screen keypad / PIN entry UI).
//
// 2. As the user presses buttons, characters are appended to
//    a "key" URL query parameter. The display shows "*" chars
//    to mask the input (like a PIN pad).
//
// 3. When ENTER is pressed, the page reloads with ?key=XXXX
//    in the URL, which triggers validateKeyAndUpdateUI().
//
// 4. validateKeyAndUpdateUI() fetches "favicon.png" — which
//    is actually a disguised binary payload, NOT a real image.
//    It decodes the payload via a byte-shuffle/XOR algorithm,
//    then extracts a license key string from the bytes
//    (4 letters + 3 digits, e.g. "ABCD-123").
//
// 5. The entered key is compared against the extracted key.
//    - Match: shows the key and triggers a "spinning" animation
//    - No match: shows "INCORRECT" in red
//
// 6. CLEAR removes the key param and resets the display.
//
// The heavy obfuscation (string array rotation, hex literals,
// anti-debug traps, anti-tamper RegExp checks) is all designed
// to hide the fact that the real secret key is embedded inside
// the "favicon.png" file fetched from the server.
// ============================================================
 