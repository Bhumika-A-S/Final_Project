import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/api.dart';
import '../main.dart';

class AiAssistantPage extends StatefulWidget {
  const AiAssistantPage({super.key});

  @override
  State<AiAssistantPage> createState() => _AiAssistantPageState();
}

class _AiAssistantPageState extends State<AiAssistantPage> {
  final _questionCtl = TextEditingController();
  String? _answer;
  List<dynamic>? _tools;
  bool _loading = false;
  String? _error;

  Future<void> _ask() async {
    final q = _questionCtl.text.trim();
    if (q.isEmpty) {
      setState(() => _error = 'Please type a question');
      return;
    }
    setState(() {
      _loading = true;
      _error = null;
      _answer = null;
      _tools = null;
    });

    try {
      final res = await api.queryAI(q);
      if (res == null) throw Exception('No response');
      setState(() {
        _answer = res['answer'] as String?;
        _tools = res['tools_used'] as List<dynamic>?;
      });
    } catch (e) {
      setState(() => _error = 'Error: $e');
    } finally {
      setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('AI Assistant')),
      drawer: Drawer(
        child: ListView(children: [
          ListTile(title: const Text('Customer'), onTap: () => Navigator.pushReplacementNamed(context, '/')),
          ListTile(title: const Text('Waiter Dashboard'), onTap: () => Navigator.pushNamed(context, '/waiter')),
          ListTile(title: const Text('Owner Dashboard'), onTap: () => Navigator.pushNamed(context, '/owner')),
          ListTile(title: const Text('Admin QR'), onTap: () => Navigator.pushNamed(context, '/admin')),
          ListTile(title: const Text('Sign out'), onTap: () {
            Provider.of<AuthModel>(context, listen: false).clear();
            Navigator.pushReplacementNamed(context, '/login');
          }),
        ]),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (_loading) const LinearProgressIndicator(),
            if (_error != null) Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(color: Colors.red.shade100, borderRadius: BorderRadius.circular(8)),
              child: Text(_error!, style: TextStyle(color: Colors.red.shade900)),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: _questionCtl,
              decoration: const InputDecoration(
                labelText: 'Ask a question',
                border: OutlineInputBorder(),
              ),
              onSubmitted: (_) => _ask(),
            ),
            const SizedBox(height: 12),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: _ask,
                child: const Text('Ask AI'),
              ),
            ),
            const SizedBox(height: 20),
            if (_answer != null) ...[
              const Text('Answer', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
              const SizedBox(height: 8),
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(color: Colors.grey.shade100, borderRadius: BorderRadius.circular(8)),
                child: Text(_answer!),
              ),
            ],
            if (_tools != null && _tools!.isNotEmpty) ...[
              const SizedBox(height: 20),
              const Text('Tools executed', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
              const SizedBox(height: 8),
              ..._tools!.map((t) {
                final name = t['tool'] ?? 'unknown';
                final args = t['args'] != null ? t['args'].toString() : '';
                return Text('- $name $args');
              }).toList(),
            ],
          ],
        ),
      ),
    );
  }
}
