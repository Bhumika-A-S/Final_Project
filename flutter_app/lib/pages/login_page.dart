import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:http/http.dart' as http;
import '../services/api.dart';
import '../main.dart';

class LoginPage extends StatefulWidget {
  const LoginPage({super.key});

  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  final _userCtl = TextEditingController();
  final _passCtl = TextEditingController();
  bool _passwordVisible = false;
  bool _loading = false;
  String? _error;

  Future<void> _login() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    final result = await api.login(_userCtl.text, _passCtl.text);
    setState(() {
      _loading = false;
    });
    if (result != null && result['access_token'] != null) {
      final auth = Provider.of<AuthModel>(context, listen: false);
      auth.update(t: result['access_token'], r: result['role'], u: _userCtl.text);
      Navigator.pushReplacementNamed(context, '/');
    } else {
      // try to ping backend root to see if server is reachable
      String msg = 'Login failed';
      try {
        final ping = await http.get(Uri.parse('${api.baseUrl}/'));
        if (ping.statusCode != 200) {
          msg = 'Backend responded ${ping.statusCode}';
        } else {
          msg = 'Invalid credentials';
        }
      } catch (e) {
        msg = 'Unable to reach backend at ${api.baseUrl}';
      }
      setState(() {
        _error = msg;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Sign In')),
      body: Center(
        child: Card(
          margin: const EdgeInsets.all(24),
          child: Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                TextField(controller: _userCtl, decoration: const InputDecoration(labelText: 'Username')),
                const SizedBox(height: 8),
                TextField(
                  controller: _passCtl,
                  obscureText: !_passwordVisible,
                  decoration: InputDecoration(
                    labelText: 'Password',
                    suffixIcon: IconButton(
                      icon: Icon(_passwordVisible ? Icons.visibility_off : Icons.visibility),
                      onPressed: () => setState(() => _passwordVisible = !_passwordVisible),
                    ),
                  ),
                ),
                if (_error != null) ...[
                  const SizedBox(height: 8),
                  Text(_error!, style: const TextStyle(color: Colors.red)),
                ],
                const SizedBox(height: 16),
                _loading ? const CircularProgressIndicator() : ElevatedButton(onPressed: _login, child: const Text('Sign in')),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
