import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;

class ApiClient {

  late final String baseUrl;
  String? _token;
  String? role;

  void setToken(String token) {
  _token = token;
}

  ApiClient({String? overrideBase}) {

    if (overrideBase != null) {
      baseUrl = overrideBase;

    } else if (kIsWeb) {
      // Flutter Web
      baseUrl = 'http://localhost:8000';

    } else {
      // Android physical device
      // ⚠️ Replace with YOUR laptop IP
      baseUrl = 'http://192.168.1.100:8000';
    }

    print("API BASE URL: $baseUrl");
  }

  Map<String, String> _headers() {
    final headers = {
      'Content-Type': 'application/json'
    };

    if (_token != null) {
      headers['Authorization'] = 'Bearer $_token';
    }

    return headers;
  }

    // signpayloa
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


  // LOGIN (staff only)
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

    if (resp.statusCode == 200) {

      final data = jsonDecode(resp.body);

      // save token
      _token = data['access_token'];

      // save role for RBAC
      role = data['role'];

      print("TOKEN SAVED: $_token");
      print("ROLE: $role");

      return data;
    }

    print("LOGIN FAILED: ${resp.body}");
    return null;

  } catch (e) {
    print("LOGIN ERROR: $e");
    return null;
  }
}

  // GET WAITERS (auth required)
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

  // CUSTOMER TIP (NO LOGIN)
  Future<Map<String, dynamic>?> submitTip(
      String waiterId,
      double amount,
      int rating,
      String feedback) async {

    final url = '$baseUrl/transactions';

    try {

      final resp = await http.post(
        Uri.parse(url),

        // ❗ DO NOT SEND TOKEN FOR CUSTOMER
        headers: {
          'Content-Type': 'application/json'
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

      print("TIP ERROR: ${resp.body}");
      return null;

    } catch (e) {
      print("TIP ERROR: $e");
      return null;
    }
  }

  // WAITER SUMMARY
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

// queryai

Future<Map<String, dynamic>?> queryAI(String q) async {

  final url = '$baseUrl/ai/query';

  try {

    final resp = await http.post(
      Uri.parse(url),
      headers: _headers(),
      body: jsonEncode({
        "query": q
      }),
    );

    if (resp.statusCode == 200) {
      return jsonDecode(resp.body);
    }

    return null;

  } catch (e) {
    print("AI ERROR: $e");
    return null;
  }
}


  // WAITER INSIGHTS
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

  // TEAM INSIGHTS (owner/admin)
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

}

final api = ApiClient();