import 'dart:convert';
import 'package:http/http.dart' as http;
import 'dart:developer' as developer;

import 'package:flutter/foundation.dart';

class ApiClient {
  late final String baseUrl;
  String? _token;

  ApiClient({String? overrideBase}) {
    if (overrideBase != null) {
      baseUrl = overrideBase;
    } else if (kIsWeb) {
      baseUrl = 'http://localhost:8000';
    } else {
      baseUrl = 'http://10.0.2.2:8000';
    }
    _log('ApiClient initialized with baseUrl: $baseUrl');
  }

  void _log(String msg) {
    developer.log('[API] $msg', name: 'TipTrack.API');
  }

  Map<String, String> _headers() {
    final headers = {'Content-Type': 'application/json'};
    if (_token != null) headers['Authorization'] = 'Bearer $_token';
    return headers;
  }

  void setToken(String? t) {
    _token = t;
    _log('Token set: ${t != null ? t.substring(0, 20) + '...' : 'null'}');
  }

  void clearToken() {
    _token = null;
    _log('Token cleared');
  }

  Future<Map<String, dynamic>?> login(String username, String password) async {
    final url = '$baseUrl/auth/login';
    _log('POST $url with username=$username');
    try {
      final resp = await http.post(
        Uri.parse(url),
        headers: _headers(),
        body: jsonEncode({'username': username, 'password': password}),
      ).timeout(const Duration(seconds: 10));
      _log('Response status: ${resp.statusCode}');
      if (resp.statusCode == 200) {
        final data = jsonDecode(resp.body) as Map<String, dynamic>;
        _log('Login successful for $username');
        return data;
      } else {
        _log('Login failed: ${resp.statusCode} ${resp.body}');
        return null;
      }
    } catch (e) {
      _log('Login error: $e');
      return null;
    }
  }

  Future<List<dynamic>> getWaiters() async {
    final url = '$baseUrl/waiters';
    _log('GET $url');
    try {
      final resp = await http.get(Uri.parse(url), headers: _headers()).timeout(const Duration(seconds: 10));
      _log('Response status: ${resp.statusCode}');
      if (resp.statusCode == 200) {
        final data = jsonDecode(resp.body) as List<dynamic>;
        _log('Fetched ${data.length} waiters');
        return data;
      } else {
        _log('Failed to fetch waiters: ${resp.statusCode} ${resp.body}');
        return [];
      }
    } catch (e) {
      _log('getWaiters error: $e');
      return [];
    }
  }

  Future<Map<String, dynamic>?> submitTip(String waiterId, double amount, int rating, String feedback) async {
    final url = '$baseUrl/transactions';
    _log('POST $url for waiter=$waiterId, amount=$amount, rating=$rating');
    try {
      final resp = await http.post(
        Uri.parse(url),
        headers: _headers(),
        body: jsonEncode({'waiter_id': waiterId, 'amount': amount, 'rating': rating, 'feedback': feedback}),
      ).timeout(const Duration(seconds: 10));
      _log('Response status: ${resp.statusCode}');
      if (resp.statusCode == 200) {
        final data = jsonDecode(resp.body) as Map<String, dynamic>;
        _log('Tip submitted successfully');
        return data;
      } else {
        _log('Tip submission failed: ${resp.statusCode} ${resp.body}');
        return null;
      }
    } catch (e) {
      _log('submitTip error: $e');
      return null;
    }
  }

  Future<Map<String, dynamic>?> getWaiterSummary(String waiterId) async {
    final url = '$baseUrl/waiters/$waiterId/summary';
    _log('GET $url');
    try {
      final resp = await http.get(Uri.parse(url), headers: _headers()).timeout(const Duration(seconds: 10));
      _log('Response status: ${resp.statusCode}');
      if (resp.statusCode == 200) {
        final data = jsonDecode(resp.body) as Map<String, dynamic>;
        _log('Fetched waiter summary: $data');
        return data;
      } else {
        _log('Failed to fetch summary: ${resp.statusCode} ${resp.body}');
        return null;
      }
    } catch (e) {
      _log('getWaiterSummary error: $e');
      return null;
    }
  }

  Future<Map<String, dynamic>?> getWaiterInsights(String waiterId) async {
    final url = '$baseUrl/insights/waiter/$waiterId';
    _log('GET $url');
    try {
      final resp = await http.get(Uri.parse(url), headers: _headers()).timeout(const Duration(seconds: 10));
      _log('Response status: ${resp.statusCode}');
      if (resp.statusCode == 200) {
        final data = jsonDecode(resp.body) as Map<String, dynamic>;
        _log('Fetched waiter insights');
        return data;
      } else {
        _log('Failed to fetch insights: ${resp.statusCode} ${resp.body}');
        return null;
      }
    } catch (e) {
      _log('getWaiterInsights error: $e');
      return null;
    }
  }

  Future<Map<String, dynamic>?> getTeamInsights() async {
    final url = '$baseUrl/insights/team';
    _log('GET $url');
    try {
      final resp = await http.get(Uri.parse(url), headers: _headers()).timeout(const Duration(seconds: 10));
      _log('Response status: ${resp.statusCode}');
      if (resp.statusCode == 200) {
        final data = jsonDecode(resp.body) as Map<String, dynamic>;
        _log('Fetched team insights: total_orders=${data['total_orders']}');
        return data;
      } else {
        _log('Failed to fetch team insights: ${resp.statusCode} ${resp.body}');
        return null;
      }
    } catch (e) {
      _log('getTeamInsights error: $e');
      return null;
    }
  }

  Future<Map<String, dynamic>?> queryAI(String question) async {
    final url = '$baseUrl/ai/query';
    _log('POST $url question=$question');
    try {
      final resp = await http.post(
        Uri.parse(url),
        headers: _headers(),
        body: jsonEncode({'question': question}),
      ).timeout(const Duration(seconds: 20));
      _log('Response status: ${resp.statusCode}');
      if (resp.statusCode == 200) {
        final data = jsonDecode(resp.body) as Map<String, dynamic>;
        _log('AI response received');
        return data;
      } else {
        _log('AI query failed: ${resp.statusCode} ${resp.body}');
        return null;
      }
    } catch (e) {
      _log('queryAI error: $e');
      return null;
    }
  }

  Future<Map<String, dynamic>?> signPayload(Map<String, dynamic> payload) async {
    final url = '$baseUrl/qr/sign';
    _log('POST $url with payload: $payload');
    try {
      final resp = await http.post(
        Uri.parse(url),
        headers: _headers(),
        body: jsonEncode(payload),
      ).timeout(const Duration(seconds: 10));
      _log('Response status: ${resp.statusCode}');
      if (resp.statusCode == 200) {
        final data = jsonDecode(resp.body) as Map<String, dynamic>;
        _log('Payload signed successfully');
        return data;
      } else {
        _log('Signing failed: ${resp.statusCode} ${resp.body}');
        return null;
      }
    } catch (e) {
      _log('signPayload error: $e');
      return null;
    }
  }
}

final api = ApiClient();
