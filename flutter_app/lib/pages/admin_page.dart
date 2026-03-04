import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:http/http.dart' as http;
import '../services/api.dart';
import '../main.dart';

class AdminPage extends StatefulWidget {
  const AdminPage({super.key});

  @override
  State<AdminPage> createState() => _AdminPageState();
}

class _AdminPageState extends State<AdminPage> {
  final _baseUrlCtl = TextEditingController(text: 'http://localhost:8501/');
  final _waiterCtl = TextEditingController();
  bool _checking = false;
  String? _backendStatus;

  Future<void> _checkBackend() async {
    setState(() => _checking = true);
    try {
      final resp = await http.get(Uri.parse('${api.baseUrl}/')).timeout(const Duration(seconds: 5));
      setState(() => _backendStatus = 'Backend OK (${resp.statusCode})');
    } catch (e) {
      setState(() => _backendStatus = 'Backend unreachable: $e');
    } finally {
      setState(() => _checking = false);
    }
  }

  Future<void> _sign() async {
    final waiterId = _waiterCtl.text.trim();
    if (waiterId.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(
        content: Text('Enter waiter ID'),
        backgroundColor: Colors.red,
      ));
      return;
    }
    final signed = await api.signPayload({'waiter_id': waiterId});
    if (signed != null) {
      final payload = signed['payload'];
      final sig = signed['signature'];
      final url = '${_baseUrlCtl.text}${_baseUrlCtl.text.contains('?') ? '&' : '?'}p=$payload&s=$sig';
      showDialog(
        context: context,
        builder: (_) => AlertDialog(
          title: const Text('Signed QR Link'),
          content: SingleChildScrollView(
            child: SelectableText(url),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Close'),
            ),
          ],
        ),
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(
        content: Text('Signing failed (admin privileges required)'),
        backgroundColor: Colors.red,
      ));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Admin · QR')),
      drawer: Drawer(
        child: ListView(children: [
          ListTile(title: const Text('Customer'), onTap: () => Navigator.pushReplacementNamed(context, '/')),
          ListTile(title: const Text('Waiter Dashboard'), onTap: () => Navigator.pushNamed(context, '/waiter')),
          ListTile(title: const Text('Owner Dashboard'), onTap: () => Navigator.pushNamed(context, '/owner')),
          ListTile(title: const Text('AI Assistant'), onTap: () => Navigator.pushNamed(context, '/ai')),
          ListTile(title: const Text('Sign out'), onTap: () {
            Provider.of<AuthModel>(context, listen: false).clear();
            Navigator.pushReplacementNamed(context, '/login');
          }),
        ]),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Card(
                child: ListTile(
                  title: const Text('Backend Status'),
                  subtitle: Text(_backendStatus ?? 'Not checked'),
                  trailing: _checking
                      ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2))
                      : IconButton(
                          icon: const Icon(Icons.refresh),
                          onPressed: _checkBackend,
                        ),
                ),
              ),
              const SizedBox(height: 20),
              const Text('QR Code Generator', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
              const SizedBox(height: 12),
              TextField(
                controller: _baseUrlCtl,
                decoration: const InputDecoration(
                  labelText: 'App base URL',
                  border: OutlineInputBorder(),
                  helperText: 'Base URL for Streamlit app',
                ),
              ),
              const SizedBox(height: 12),
              TextField(
                controller: _waiterCtl,
                decoration: const InputDecoration(
                  labelText: 'Waiter ID',
                  border: OutlineInputBorder(),
                  helperText: 'Waiter ID to encode in QR',
                ),
              ),
              const SizedBox(height: 16),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: _sign,
                  child: const Text('Create Signed URL'),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
