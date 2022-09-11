const _ = require('lodash');
const fs = require('fs');
const qs = require('querystring');
const jwt = require('jsonwebtoken');

var security = {};

// Verify & Decode JWS or JWT
security.verifyJWS = function verifyJWS(jws, publicCert) {
  // verify token
  // ignore notbefore check because it gives errors sometimes if the call is too fast.
  try {
    var decoded = jwt.verify(jws, fs.readFileSync(publicCert, 'utf8'), {
      algorithms: ['RS256'],
      ignoreNotBefore: true
    });
    return decoded;
  } catch (error) {
    console.error("Error with verifying and decoding JWS: %s".red, error);
    throw ("Error with verifying and decoding JWS");
  }
}

module.exports = security;
