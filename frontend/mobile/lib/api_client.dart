import 'dart:convert';
import 'dart:typed_data';

import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;

class ApiClient {
  ApiClient({String? baseUrl})
      : baseUrl = baseUrl ??
            const String.fromEnvironment('API_BASE_URL',
                defaultValue: 'https://rakshak-backend-7qx2.onrender.com');

  static final instance = ApiClient();
  final String baseUrl;
  final FlutterSecureStorage _secureStorage = const FlutterSecureStorage();
  String? _accessToken;

  Future<Map<String, dynamic>> login(
      String emailOrPhone, String password) async {
    final response = await http
        .post(_uri('/api/v1/auth/login'),
            headers: _jsonHeaders(),
            body: jsonEncode(
                {'email_or_phone': emailOrPhone, 'password': password}))
        .timeout(const Duration(seconds: 30));
    final body = _decode(response);
    _ensureSuccess(response, body);
    _accessToken = body['access_token'] as String?;
    if (_accessToken != null) {
      await _secureStorage.write(key: 'access_token', value: _accessToken);
    }
    if (body['refresh_token'] is String) {
      await _secureStorage.write(
          key: 'refresh_token', value: body['refresh_token'] as String);
    }
    return body;
  }

  Future<Map<String, dynamic>> register(
      {required String name,
      required String email,
      required String phone,
      required String password,
      required bool consentToDataProcessing}) async {
    final response = await http
        .post(_uri('/api/v1/auth/register'),
            headers: _jsonHeaders(),
            body: jsonEncode({
              'display_name': name,
              'email': email,
              if (phone.isNotEmpty) 'phone': phone,
              'password': password,
              'role': 'farmer',
              'consent_to_data_processing': consentToDataProcessing
            }))
        .timeout(const Duration(seconds: 30));
    final body = _decode(response);
    _ensureSuccess(response, body);
    return body as Map<String, dynamic>;
  }

  Future<bool> restoreSession() async {
    _accessToken = await _secureStorage.read(key: 'access_token');
    if (_accessToken == null) return false;
    try {
      await currentUser();
      return true;
    } on ApiException catch (error) {
      if (error.statusCode == 401 || error.statusCode == 403) {
        await signOut();
        return false;
      }
      return true;
    } catch (_) {
      return true;
    }
  }

  Future<bool> refreshSession() async {
    final refresh = await _secureStorage.read(key: 'refresh_token');
    if (refresh == null) return false;
    try {
      final response = await http
          .post(_uri('/api/v1/auth/refresh'),
              headers: _jsonHeaders(),
              body: jsonEncode({'refresh_token': refresh}))
          .timeout(const Duration(seconds: 30));
      final body = _decode(response);
      _ensureSuccess(response, body);
      _accessToken = body['access_token'] as String?;
      if (_accessToken != null) {
        await _secureStorage.write(key: 'access_token', value: _accessToken);
      }
      return _accessToken != null;
    } on ApiException catch (error) {
      if (error.statusCode == 401 || error.statusCode == 403) await signOut();
      return false;
    } catch (_) {
      return false;
    }
  }

  Future<Map<String, dynamic>> currentUser() async =>
      (await _get('/api/v1/auth/me')) as Map<String, dynamic>;
  Future<List<Map<String, dynamic>>> listFarms() async =>
      _getAll('/api/v1/farms');
  Future<Map<String, dynamic>> createFarm(String name) async =>
      (await _post('/api/v1/farms', {'name': name})) as Map<String, dynamic>;
  Future<Map<String, dynamic>> createField(
          String farmId, String name, double? area) async =>
      (await _post('/api/v1/farms/$farmId/fields', {
        'name': name,
        if (area != null) 'area_hectares': area
      })) as Map<String, dynamic>;
  Future<Map<String, dynamic>> updateProfile(
          Map<String, dynamic> payload) async =>
      (await _patch('/api/v1/auth/me', payload)) as Map<String, dynamic>;
  Future<void> logoutAll() async {
    await _post('/api/v1/auth/logout-all', {});
    await signOut();
  }

  Future<void> changePassword(String current, String next) async {
    await _post('/api/v1/auth/password',
        {'current_password': current, 'new_password': next});
    await signOut();
  }

  Map<String, String> get mediaHeaders => _authHeaders();
  Future<Uint8List> evidenceBytes(String path) async {
    if (!path.startsWith('/api/v1/videos/')) {
      throw ArgumentError('Invalid evidence path');
    }
    var response = await http
        .get(_uri(path), headers: _authHeaders())
        .timeout(const Duration(seconds: 45));
    if (response.statusCode == 401 && await refreshSession()) {
      response = await http
          .get(_uri(path), headers: _authHeaders())
          .timeout(const Duration(seconds: 45));
    }
    if (response.statusCode != 200) _ensureSuccess(response, _decode(response));
    return response.bodyBytes;
  }

  Future<List<Map<String, dynamic>>> listFields() async =>
      _getAll('/api/v1/fields');
  Future<List<Map<String, dynamic>>> listVideos({String? fieldId}) => _getAll(
      '/api/v1/videos${fieldId == null ? '' : '?field_id=${Uri.encodeQueryComponent(fieldId)}'}');
  Future<List<Map<String, dynamic>>> _getAll(String path) async {
    final records = <Map<String, dynamic>>[];
    for (var offset = 0;; offset += 100) {
      final page = (await _get(
                  '$path${path.contains('?') ? '&' : '?'}limit=100&offset=$offset')
              as List)
          .cast<Map<String, dynamic>>();
      records.addAll(page);
      if (page.length < 100) {
        return records;
      }
    }
  }

  Future<Map<String, dynamic>> uploadVideo(
      {required String fieldId,
      required String filePath,
      required bool consent}) async {
    final request = http.MultipartRequest('POST', _uri('/api/v1/videos'));
    request.headers.addAll(_authHeaders());
    request.fields['field_id'] = fieldId;
    request.fields['consent'] = consent.toString();
    request.files.add(await http.MultipartFile.fromPath('file', filePath));
    final response = await http.Response.fromStream(
            await request.send().timeout(const Duration(minutes: 3)))
        .timeout(const Duration(minutes: 3));
    final body = _decode(response);
    _ensureSuccess(response, body);
    return body as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> videoStatus(String videoId) async =>
      (await _get('/api/v1/videos/$videoId/status')) as Map<String, dynamic>;
  Future<Map<String, dynamic>> videoAnalysis(String videoId) async =>
      (await _get('/api/v1/videos/$videoId/analysis')) as Map<String, dynamic>;
  Future<Map<String, dynamic>> diagnosis(String diagnosisId) async =>
      (await _get('/api/v1/diagnosis/$diagnosisId')) as Map<String, dynamic>;
  Future<List<Map<String, dynamic>>> evidenceFrames(String videoId) async =>
      (await _get('/api/v1/videos/$videoId/frames'))
          .cast<Map<String, dynamic>>();
  Future<Map<String, dynamic>> submitFeedback(String diagnosisId,
          {required String correctionType, String? note}) async =>
      (await _post('/api/v1/diagnosis/$diagnosisId/feedback', {
        'correction_type': correctionType,
        'note': note
      })) as Map<String, dynamic>;
  Future<Map<String, dynamic>> retryVideo(String videoId) async =>
      (await _post('/api/v1/videos/$videoId/retry', {}))
          as Map<String, dynamic>;
  Future<Map<String, dynamic>> requestReview(String diagnosisId) async =>
      (await _post('/api/v1/diagnosis/$diagnosisId/review-requests', {}))
          as Map<String, dynamic>;

  Future<void> signOut() async {
    _accessToken = null;
    await _secureStorage.deleteAll();
  }

  Future<dynamic> _get(String path) async {
    var response = await http
        .get(_uri(path), headers: _authHeaders())
        .timeout(const Duration(seconds: 30));
    if (response.statusCode == 401 && await refreshSession()) {
      response = await http
          .get(_uri(path), headers: _authHeaders())
          .timeout(const Duration(seconds: 30));
    }
    final body = _decode(response);
    _ensureSuccess(response, body);
    return body;
  }

  Future<dynamic> _post(String path, Map<String, dynamic> payload) async {
    var response = await http
        .post(_uri(path),
            headers: {..._jsonHeaders(), ..._authHeaders()},
            body: jsonEncode(payload))
        .timeout(const Duration(seconds: 30));
    if (response.statusCode == 401 && await refreshSession()) {
      response = await http
          .post(_uri(path),
              headers: {..._jsonHeaders(), ..._authHeaders()},
              body: jsonEncode(payload))
          .timeout(const Duration(seconds: 30));
    }
    final body = _decode(response);
    _ensureSuccess(response, body);
    return body;
  }

  Future<dynamic> _patch(String path, Map<String, dynamic> payload) async {
    var response = await http
        .patch(_uri(path),
            headers: {..._jsonHeaders(), ..._authHeaders()},
            body: jsonEncode(payload))
        .timeout(const Duration(seconds: 30));
    if (response.statusCode == 401 && await refreshSession()) {
      response = await http
          .patch(_uri(path),
              headers: {..._jsonHeaders(), ..._authHeaders()},
              body: jsonEncode(payload))
          .timeout(const Duration(seconds: 30));
    }
    final body = _decode(response);
    _ensureSuccess(response, body);
    return body;
  }

  Uri _uri(String path) => Uri.parse('$baseUrl$path');
  Map<String, String> _jsonHeaders() =>
      {'Content-Type': 'application/json', 'Accept': 'application/json'};
  Map<String, String> _authHeaders() =>
      _accessToken == null ? {} : {'Authorization': 'Bearer $_accessToken'};
  dynamic _decode(http.Response response) {
    try {
      return jsonDecode(response.body);
    } catch (_) {
      return {'detail': response.body};
    }
  }

  void _ensureSuccess(http.Response response, dynamic body) {
    if (response.statusCode >= 200 && response.statusCode < 300) return;
    throw ApiException(
        body is Map
            ? (body['message'] ?? body['detail'])?.toString() ??
                'Request failed'
            : 'Request failed',
        response.statusCode);
  }
}

class ApiException implements Exception {
  const ApiException(this.message, this.statusCode);
  final String message;
  final int statusCode;
  @override
  String toString() => message;
}

String safeErrorMessage(Object error, {String fallback = 'Please try again.'}) {
  if (error is ApiException) {
    if (error.statusCode == 401) {
      return 'Your sign-in has expired. Please sign in again.';
    }
    if (error.statusCode == 403) {
      return 'Your account does not have access to this action.';
    }
    if (error.statusCode >= 500) {
      return 'The service is temporarily unavailable. Please try again.';
    }
  }
  return fallback;
}
