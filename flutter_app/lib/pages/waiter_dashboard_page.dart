import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/api.dart';
import '../main.dart';

class WaiterDashboardPage extends StatefulWidget {
  const WaiterDashboardPage({super.key});

  @override
  State<WaiterDashboardPage> createState() => _WaiterDashboardPageState();
}

class _WaiterDashboardPageState extends State<WaiterDashboardPage> {
  final _waiterCtl = TextEditingController();
  Map<String, dynamic>? _summary;
  Map<String, dynamic>? _insights;
  bool _loading = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final auth = Provider.of<AuthModel>(context, listen: false);
      if (auth.role == 'waiter' && auth.username != null) {
        _waiterCtl.text = auth.username!;
        _fetch();
      }
    });
  }

  Future<void> _fetch() async {
    final id = _waiterCtl.text.trim();
    if (id.isEmpty) {
      setState(() => _error = 'Enter waiter ID');
      return;
    }
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final s = await api.getWaiterSummary(id);
      final i = await api.getWaiterInsights(id);
      if (s == null && i == null) throw Exception('No data found for waiter $id');
      setState(() {
        _summary = s;
        _insights = i;
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
      appBar: AppBar(title: const Text('Waiter Dashboard')),
      drawer: Drawer(
        child: ListView(children: [
          ListTile(title: const Text('Customer'), onTap: () => Navigator.pushReplacementNamed(context, '/')),
          ListTile(title: const Text('Owner Dashboard'), onTap: () => Navigator.pushNamed(context, '/owner')),
          ListTile(title: const Text('Admin QR'), onTap: () => Navigator.pushNamed(context, '/admin')),
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
              if (_loading) const LinearProgressIndicator(),
              if (_error != null) Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(color: Colors.red.shade100, borderRadius: BorderRadius.circular(8)),
                child: Text(_error!, style: TextStyle(color: Colors.red.shade900)),
              ),
              const SizedBox(height: 16),
              TextField(
                controller: _waiterCtl,
                decoration: const InputDecoration(
                  labelText: 'Waiter ID',
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 12),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: _fetch,
                  child: const Text('Load Data'),
                ),
              ),
              const SizedBox(height: 20),
              if (_summary != null) ...[
                const Text('Summary', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                const SizedBox(height: 12),
                Card(
                  child: ListTile(
                    title: const Text('Total Tips'),
                    subtitle: Text('\$${_summary!['total_tips']?.toStringAsFixed(2) ?? '0.00'}'),
                  ),
                ),
                const SizedBox(height: 8),
                Card(
                  child: ListTile(
                    title: const Text('Average Rating'),
                    subtitle: Text('${_summary!['avg_rating']?.toStringAsFixed(2) ?? '0.00'} / 5'),
                  ),
                ),
                const SizedBox(height: 8),
                Card(
                  child: ListTile(
                    title: const Text('Number of Tips'),
                    subtitle: Text('${_summary!['num_tips'] ?? 0}'),
                  ),
                ),
              ],
              const SizedBox(height: 20),
              if (_insights != null) ...[
                const Text('Performance Insights', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                const SizedBox(height: 12),
                Card(
                  child: ListTile(
                    title: const Text('Performance Score'),
                    subtitle: Text('${_insights!['score'] ?? 0} / 100'),
                  ),
                ),
                const SizedBox(height: 8),
                Card(
                  child: ListTile(
                    title: const Text('Trend'),
                    subtitle: Text('${_insights!['trend'] ?? 'stable'}'),
                  ),
                ),
                if (((_insights?['recommendations'] as List?)?.isNotEmpty ?? false)) ...[
                  const SizedBox(height: 12),
                  const Text('Recommendations', style: TextStyle(fontWeight: FontWeight.bold)),
                  const SizedBox(height: 8),
                  for (var rec in (_insights!['recommendations'] as List))
                    Padding(
                      padding: const EdgeInsets.only(bottom: 8.0),
                      child: Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text('• ', style: TextStyle(fontWeight: FontWeight.bold)),
                          Expanded(child: Text(rec.toString())),
                        ],
                      ),
                    ),
                ]
              ] else if (!_loading && _summary == null && _error == null)
                const Text('Enter a waiter ID and click "Load Data" to fetch insights'),
            ],
          ),
        ),
      ),
    );
  }
}
