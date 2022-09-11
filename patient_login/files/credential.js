const dotenv = require('dotenv').config()
var express = require('express');
const restClient = require('superagent-bluebird-promise');
const path = require('path');
const _ = require('lodash');
const querystring = require('querystring');
const securityHelper = require('../security/security');
var bodyParser = require('body-parser');
var cookieParser = require('cookie-parser');
var cors = require('cors')

var router = express.Router();
var app = express();

app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: false }));
app.use(cookieParser());
app.use(cors())
app.options('*', cors())
app.use("/",router)

// view engine setup
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'pug');

process.env.NODE_TLS_REJECT_UNAUTHORIZED = "0";

// Setup Configuration
// LOADED FRON ENV VARIABLE: public key from MyInfo Consent Platform given to you during onboarding for RSA digital signature
var _publicCertContent = process.env.MYINFO_SIGNATURE_CERT_PUBLIC_CERT;
// LOADED FRON ENV VARIABLE: your private key for RSA digital signature
var _privateKeyContent = process.env.DEMO_APP_SIGNATURE_CERT_PRIVATE_KEY;
// LOADED FRON ENV VARIABLE: your client_id provided to you during onboarding
var _clientId = process.env.MYINFO_APP_CLIENT_ID;
// LOADED FRON ENV VARIABLE: your client_secret provided to you during onboarding
var _clientSecret = process.env.MYINFO_APP_CLIENT_SECRET;
// redirect URL for your web application
var _redirectUrl = process.env.MYINFO_APP_REDIRECT_URL;

// URLs for MyInfo APIs
var _authLevel = process.env.AUTH_LEVEL;
var _authApiUrl = process.env.MYINFO_API_AUTHORISE;
var _tokenApiUrl = process.env.MYINFO_API_TOKEN;
var _personApiUrl = process.env.MYINFO_API_PERSON;

//attributes patientMS needs
var _attributes = "uinfin,name,mobileno,regadd";

/* GET home page. */
router.get('/', function(req, res) {
  res.sendFile((path.join(__dirname + "/patientLogIn.html")));
});

// callback function - directs back to home page
router.get('/callback', function(req, res) {
  res.sendFile((path.join(__dirname + "/patientLogIn.html")));
});

// function for getting environment variables to the frontend
router.get('/getEnv', function(req, res, next) {
  if (_clientId == undefined || _clientId == null)
    res.jsonp({
      status: "ERROR",
      msg: "client_id not found"
    });
  else
    res.jsonp({
      status: "OK",
      clientId: _clientId,
      redirectUrl: _redirectUrl,
      authApiUrl: _authApiUrl,
      attributes: _attributes,
      authLevel: _authLevel
    });
});

// function for frontend to call backend
router.post('/getPersonData', function(req, res, next) {
  // get variables from frontend
  var code = req.body.code;
  
  var data;
  var request;

  // **** CALL TOKEN API ****
  request = createTokenRequest(code);
  request
    .buffer(true)
    .end(function(callErr, callRes) {
      if (callErr) {
        // ERROR
        res.jsonp({
          status: "ERROR",
          msg: callErr
        });
      } 
      else {
        // SUCCESSFUL
        var data = {
          body: callRes.body,
          text: callRes.text
        };

        var accessToken = data.body.access_token;
        if (accessToken == undefined || accessToken == null) {
          res.jsonp({
            status: "ERROR",
            msg: "ACCESS TOKEN NOT FOUND"
          });
        }

        callPersonAPI(accessToken, res);
      }
    });
});

function callPersonAPI(accessToken, res) {

  // validate and decode token to get SUB
  var decoded = securityHelper.verifyJWS(accessToken, _publicCertContent);
  if (decoded == undefined || decoded == null) {
    res.jsonp({
      status: "ERROR",
      msg: "INVALID TOKEN"
    })
  }

  var sub = decoded.sub;
  if (sub == undefined || sub == null) {
    res.jsonp({
      status: "ERROR",
      msg: "SUB NOT FOUND"
    });
  }

  // **** CALL PERSON API ****
  var request = createPersonRequest(sub, accessToken);

  // Invoke asynchronous call
  request
    .buffer(true)
    .end(function(callErr, callRes) {
      if (callErr) {
        console.error("Person Call Error: ",callErr.status);
        console.error(callErr.response.req.res.text);
        res.jsonp({
          status: "ERROR",
          msg: callErr
        });
      } 
      else {
        // SUCCESSFUL
        var data = {
          body: callRes.body,
          text: callRes.text
        };
        var personData = data.text;
        if (personData == undefined || personData == null) {
          res.jsonp({
            status: "ERROR",
            msg: "PERSON DATA NOT FOUND"
          });
        } 
        else {
          personData = JSON.parse(personData);

          if (personData == undefined || personData == null) {
            res.jsonp({
              status: "ERROR",
              msg: "INVALID DATA OR SIGNATURE FOR PERSON DATA"
            });
          }
          
          res.jsonp({
            status: "OK",
            text: personData
          });

          
        } 
      }
    });
}

// function to prepare request for TOKEN API
function createTokenRequest(code) {
  var cacheCtl = "no-cache";
  var contentType = "application/x-www-form-urlencoded";
  var method = "POST";

  // assemble params for Token API
  var strParams = "grant_type=authorization_code" +
    "&code=" + code +
    "&redirect_uri=" + _redirectUrl +
    "&client_id=" + _clientId +
    "&client_secret=" + _clientSecret;
  var params = querystring.parse(strParams);

  // assemble headers for Token API
  var strHeaders = "Content-Type=" + contentType + "&Cache-Control=" + cacheCtl;
  var headers = querystring.parse(strHeaders);

  // Add Authorisation headers for connecting to API Gateway
  var authHeaders = null;

  if (!_.isEmpty(authHeaders)) {
    _.set(headers, "Authorization", authHeaders);
  }

  var request = restClient.post(_tokenApiUrl);

  // Set headers
  if (!_.isUndefined(headers) && !_.isEmpty(headers))
    request.set(headers);

  // Set Params
  if (!_.isUndefined(params) && !_.isEmpty(params))
    request.send(params);

  return request;
}

// function to prepare request for PERSON API
function createPersonRequest(sub, validToken) {
  var url = _personApiUrl + "/" + sub + "/";
  var cacheCtl = "no-cache";
  var method = "GET";

  // assemble params for Person API
  var strParams = "client_id=" + _clientId +
    "&attributes=" + _attributes;

  var params = querystring.parse(strParams);

  // assemble headers for Person API
  var strHeaders = "Cache-Control=" + cacheCtl;
  var headers = querystring.parse(strHeaders);

  _.set(headers, "Authorization", "" + ",Bearer " + validToken);

  // invoke person API
  var request = restClient.get(url);

  // Set headers
  if (!_.isUndefined(headers) && !_.isEmpty(headers))
    request.set(headers);

  // Set Params
  if (!_.isUndefined(params) && !_.isEmpty(params))
    request.query(params);

  return request;
}

module.exports = router;
module.exports = app;
