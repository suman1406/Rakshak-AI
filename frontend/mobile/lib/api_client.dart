import 'dart:convert';

import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;

class ApiClient {
  ApiClient({String? baseUrl}) : baseUrl = baseUrl ?? const String.fromEnvironment('API_BASE_URL', defaultValue: 'https://rakshak-backend-7qx2.onrender.com');

  static final instance = ApiClient();
  final String baseUrl;
  final FlutterSecureStorage _secureStorage = const FlutterSecureStorage();
  String? _accessToken;

  Future<Map<String, dynamic>> login(String emailOrPhone, String password) async {
    final response = await http.post(_uri('/api/v1/auth/login'), headers: _jsonHeaders(), body: jsonEncode({'email_or_phone': emailOrPhone, 'password': password}));
    final body = _decode(response);
    _ensureSuccess(response, body);
    _accessToken = body['access_token'] as String?;
    if (_accessToken != null) await _secureStorage.write(key: 'access_token', value: _accessToken);
    if (body['refresh_token'] is String) await _secureStorage.write(key: 'refresh_token', value: body['refresh_token'] as String);
    return body;
  }

  Future<Map<String, dynamic>> register({required String name, required String email, required String phone, required String password, required bool consentToDataProcessing}) async {
    final response = await http.post(_uri('/api/v1/auth/register'), headers: _jsonHeaders(), body: jsonEncode({'display_name': name, 'email': email, 'phone': phone, 'password': password, 'role': 'farmer', 'consent_to_data_processing': consentToDataProcessing}));
    final body = _decode(response);
    _ensureSuccess(response, body);
    return body as Map<String, dynamic>;
  }

  Future<bool> restoreSession() async {
    _accessToken = await _secureStorage.read(key: 'access_token');
    if (_accessToken == null) return false;
    try { await currentUser(); return true; } catch (_) { await signOut(); return false; }
  }

  Future<bool> refreshSession() async {
    final refresh = await _secureStorage.read(key: 'refresh_token');
    if (refresh == null) return false;
    try {
      final response = await http.post(_uri('/api/v1/auth/refresh'), headers: _jsonHeaders(), body: jsonEncode({'refresh_token': refresh}));
      final body = _decode(response);
      _ensureSuccess(response, body);
      _accessToken = body['access_token'] as String?;
      if (_accessToken != null) await _secureStorage.write(key: 'access_token', value: _accessToken);
      return _accessToken != null;
    } catch (_) {
      await signOut();
      return false;
    }
  }

  Future<Map<String, dynamic>> currentUser() async => (await _get('/api/v1/auth/me')) as Map<String, dynamic>;
  Future<Map<String, dynamic>> updateProfile(Map<String, dynamic> payload) async => (await _patch('/api/v1/auth/me', payload)) as Map<String, dynamic>;
  Map<String, String> get mediaHeaders => _authHeaders();
  Future<List<Map<String, dynamic>>> listFields() async => (await _get('/api/v1/fields')).cast<Map<String, dynamic>>();
  Future<List<Map<String, dynamic>>> listVideos({String? fieldId}) async => (await _get('/api/v1/videos${fieldId == null ? '' : '?field_id=${Uri.encodeQueryComponent(fieldId)}'}')).cast<Map<String, dynamic>>();

  Future<Map<String, dynamic>> uploadVideo({required String fieldId, required String filePath, required bool consent}) async {
    final request = http.MultipartRequest('POST', _uri('/api/v1/videos'));
    request.headers.addAll(_authHeaders());
    request.fields['field_id'] = fieldId;
    request.fields['consent'] = consent.toString();
    request.files.add(await http.MultipartFile.fromPath('file', filePath));
    final response = await http.Response.fromStream(await request.send());
    final body = _decode(response);
    _ensureSuccess(response, body);
    return body as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> videoStatus(String videoId) async => (await _get('/api/v1/videos/$videoId/status')) as Map<String, dynamic>;
  Future<Map<String, dynamic>> videoAnalysis(String videoId) async => (await _get('/api/v1/videos/$videoId/analysis')) as Map<String, dynamic>;
  Future<Map<String, dynamic>> diagnosis(String diagnosisId) async => (await _get('/api/v1/diagnosis/$diagnosisId')) as Map<String, dynamic>;
  Future<List<Map<String, dynamic>>> evidenceFrames(String videoId) async => (await _get('/api/v1/videos/$videoId/frames')).cast<Map<String, dynamic>>();
  Future<Map<String, dynamic>> submitFeedback(String diagnosisId, {required String correctionType, String? note}) async => (await _post('/api/v1/diagnosis/$diagnosisId/feedback', {'correction_type': correctionType, 'note': note})) as Map<String, dynamic>;
  Future<Map<String, dynamic>> requestReview(String diagnosisId) async => (await _post('/api/v1/diagnosis/$diagnosisId/review-requests', {})) as Map<String, dynamic>;

  Future<void> signOut() async { _accessToken = null; await _secureStorage.deleteAll(); }

  Future<dynamic> _get(String path) async {
    var response = await http.get(_uri(path), headers: _authHeaders());
    if (response.statusCode == 401 && await refreshSession()) {
      response = await http.get(_uri(path), headers: _authHeaders());
    }
    final body = _decode(response); _ensureSuccess(response, body); return body;
  }

  Future<dynamic> _post(String path, Map<String, dynamic> payload) async {
    var response = await http.post(_uri(path), headers: {..._jsonHeaders(), ..._authHeaders()}, body: jsonEncode(payload));
    if (response.statusCode == 401 && await refreshSession()) {
      response = await http.post(_uri(path), headers: {..._jsonHeaders(), ..._authHeaders()}, body: jsonEncode(payload));
    }
    final body = _decode(response); _ensureSuccess(response, body); return body;
  }

  Future<dynamic> _patch(String path, Map<String, dynamic> payload) async {
    var response = await http.patch(_uri(path), headers: {..._jsonHeaders(), ..._authHeaders()}, body: jsonEncode(payload));
    if (response.statusCode == 401 && await refreshSession()) response = await http.patch(_uri(path), headers: {..._jsonHeaders(), ..._authHeaders()}, body: jsonEncode(payload));
    final body = _decode(response); _ensureSuccess(response, body); return body;
  }

  Uri _uri(String path) => Uri.parse('$baseUrl$path');
  Map<String, String> _jsonHeaders() => {'Content-Type': 'application/json', 'Accept': 'application/json'};
  Map<String, String> _authHeaders() => _accessToken == null ? {} : {'Authorization': 'Bearer $_accessToken'};
  dynamic _decode(http.Response response) { try { return jsonDecode(response.body); } catch (_) { return {'detail': response.body}; } }
  void _ensureSuccess(http.Response response, dynamic body) { if (response.statusCode >= 200 && response.statusCode < 300) return; throw ApiException(body is Map ? (body['message'] ?? body['detail'])?.toString() ?? 'Request failed' : 'Request failed', response.statusCode); }
}

class ApiException implements Exception {
  const ApiException(this.message, this.statusCode);
  final String message;
  final int statusCode;
  @override String toString() => message;
}

String safeErrorMessage(Object error, {String fallback = 'Please try again.'}) {
  if (error is ApiException) {
    if (error.statusCode == 401) return 'Your sign-in has expired. Please sign in again.';
    if (error.statusCode == 403) return 'Your account does not have access to this action.';
    if (error.statusCode >= 500) return 'The service is temporarily unavailable. Please try again.';
  }
  return fallback;
}
