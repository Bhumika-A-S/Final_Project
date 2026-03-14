import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;

class ApiClient {

  late final String baseUrl;

  String? _token;
  String? role;

  // Set token from login
  void setToken(String token) {
    _token = token;
  }

  ApiClient({String? overrideBase}) {

    if (overrideBase != null) {

      baseUrl = overrideBase;

    } else {

      // Use same backend for all platforms
      baseUrl = 'http://localhost:8000';

    }

    print("API BASE URL: $baseUrl");
  }

  // Common headers
  Map<String, String> _headers() {

    final headers = {
      'Content-Type': 'application/json',
    };

    if (_token != null) {
      headers['Authorization'] = 'Bearer $_token';
    }

    return headers;
  }

  // ===============================
  // LOGIN
  // ===============================

  Future<Map<String, dynamic>?> login(String username, String password) async {

    final url = '$baseUrl/auth/login';

    try {

      final resp = await http.post(
        Uri.parse(url),
        headers: _headers(),
        body: jsonEncode({
          'username': username,
          'password': password
        }),
      );

      print("LOGIN STATUS: ${resp.statusCode}");
      print("LOGIN BODY: ${resp.body}");

      if (resp.statusCode == 200) {

        final data = jsonDecode(resp.body);

        _token = data['access_token'];
        role = data['role'];

        return data;
      }

      return null;

    } catch (e) {

      print("LOGIN ERROR: $e");
      return null;
    }
  }

  // ===============================
  // GET WAITERS
  // ===============================

  Future<List<dynamic>> getWaiters() async {

    final url = '$baseUrl/waiters';

    try {

      final resp = await http.get(
        Uri.parse(url),
        headers: _headers(),
      );

      if (resp.statusCode == 200) {
        return jsonDecode(resp.body);
      }

      return [];

    } catch (e) {

      print("GET WAITERS ERROR: $e");
      return [];
    }
  }

  // ===============================
  // CUSTOMER TIP
  // ===============================

  Future<Map<String, dynamic>?> submitTip(
      String waiterId,
      double amount,
      int rating,
      String feedback) async {

    final url = '$baseUrl/transactions';

    try {

      final resp = await http.post(
        Uri.parse(url),
        headers: {
          'Content-Type': 'application/json',
        },
        body: jsonEncode({
          'waiter_id': waiterId,
          'amount': amount,
          'rating': rating,
          'feedback': feedback
        }),
      );

      if (resp.statusCode == 200) {
        return jsonDecode(resp.body);
      }

      return null;

    } catch (e) {

      print("TIP ERROR: $e");
      return null;
    }
  }

  // ===============================
  // WAITER SUMMARY
  // ===============================

  Future<Map<String, dynamic>?> getWaiterSummary(String waiterId) async {

    final url = '$baseUrl/waiters/$waiterId/summary';

    try {

      final resp = await http.get(
        Uri.parse(url),
        headers: _headers(),
      );

      if (resp.statusCode == 200) {
        return jsonDecode(resp.body);
      }

      return null;

    } catch (e) {

      print("SUMMARY ERROR: $e");
      return null;
    }
  }

  // ===============================
  // AI QUERY
  // ===============================

  Future<Map<String, dynamic>?> queryAI(String q) async {

    final url = '$baseUrl/ai/query';

    try {

      final resp = await http.post(
        Uri.parse(url),
        headers: _headers(),
        body: jsonEncode({
          "question": q
        }),
      );

       print("AI STATUS: ${resp.statusCode}");
       print("AI BODY: ${resp.body}");

      if (resp.statusCode == 200) {
        return jsonDecode(resp.body);
      }

      return null;

    } catch (e) {

      print("AI ERROR: $e");
      return null;
    }
  }

  // ===============================
  // WAITER INSIGHTS
  // ===============================

  Future<Map<String, dynamic>?> getWaiterInsights(String waiterId) async {

    final url = '$baseUrl/insights/waiter/$waiterId';

    try {

      final resp = await http.get(
        Uri.parse(url),
        headers: _headers(),
      );

      if (resp.statusCode == 200) {
        return jsonDecode(resp.body);
      }

      return null;

    } catch (e) {

      print("INSIGHTS ERROR: $e");
      return null;
    }
  }

  // ===============================
  // TEAM INSIGHTS
  // ===============================

  Future<Map<String, dynamic>?> getTeamInsights() async {

    final url = '$baseUrl/insights/team';

    try {

      final resp = await http.get(
        Uri.parse(url),
        headers: _headers(),
      );

      if (resp.statusCode == 200) {
        return jsonDecode(resp.body);
      }

      return null;

    } catch (e) {

      print("TEAM INSIGHTS ERROR: $e");
      return null;
    }
  }

  // ===============================
  // QR SIGN
  // ===============================

  Future<Map<String, dynamic>?> signPayload(Map<String, dynamic> payload) async {

    final url = '$baseUrl/qr/sign';

    try {

      final resp = await http.post(
        Uri.parse(url),
        headers: _headers(),
        body: jsonEncode(payload),
      );

      if (resp.statusCode == 200) {
        return jsonDecode(resp.body);
      }

      return null;

    } catch (e) {

      print("SIGN ERROR: $e");
      return null;
    }
  }

}

final api = ApiClient();