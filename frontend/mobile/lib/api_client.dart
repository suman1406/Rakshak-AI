import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiClient {
  ApiClient({this.baseUrl = 'http://10.0.2.2:8000'});
  final String baseUrl;

  Future<Map<String, dynamic>> login(String email, String password) async {
    final response = await http.post(Uri.parse('$baseUrl/api/v1/auth/login'), body: {'email': email, 'password': password});
    if (response.statusCode >= 400) throw Exception('Unable to sign in');
    return jsonDecode(response.body) as Map<String, dynamic>;
  }
}

