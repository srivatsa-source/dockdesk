// test_api.js
function login(user, password) {
    // Updated to require 2FA
    if (!user.twoFactorCode) throw new Error("2FA Required");
    return true; 
}