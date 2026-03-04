import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/api.dart';
import '../main.dart';

class OwnerDashboardPage extends StatefulWidget {
  const OwnerDashboardPage({super.key});

  @override
  State<OwnerDashboardPage> createState() => _OwnerDashboardPageState();
}

class _OwnerDashboardPageState extends State<OwnerDashboardPage> {
  Map<String, dynamic>? _team;
  bool _loading = false;
  String? _error;

  Future<void> _load() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final t = await api.getTeamInsights();
      if (t == null) throw Exception('no data');
      setState(() => _team = t);
    } catch (e) {
      setState(() => _error = 'Failed to load: $e');
    } finally {
      setState(() => _loading = false);
    }
  }

  @override
  void initState() {
    super.initState();
    _load();
  }

  @override
  Widget build(BuildContext context) {
    final lb = _team?['leaderboard'] as List? ?? [];
    return Scaffold(
      appBar: AppBar(title: const Text('Owner Dashboard')),
      drawer: Drawer(
        child: ListView(children: [
          ListTile(title: const Text('Customer'), onTap: () => Navigator.pushReplacementNamed(context, '/')),
          ListTile(title: const Text('Waiter Dashboard'), onTap: () => Navigator.pushNamed(context, '/waiter')),
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
        child: RefreshIndicator(
          onRefresh: _load,
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
              Card(
                child: ListTile(
                  title: const Text('Total Orders'),
                  subtitle: Text('${_team?['total_orders'] ?? 0}', style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                ),
              ),
              const SizedBox(height: 12),
              Card(
                child: ListTile(
                  title: const Text('Team Performance Score'),
                  subtitle: Text('${(_team?['overall_score'] as num?)?.toStringAsFixed(2) ?? '0'} / 100'),
                ),
              ),
              const SizedBox(height: 12),
              Card(
                child: ListTile(
                  title: const Text('Low Ratings %'),
                  subtitle: Text('${((_team?['pct_low_ratings'] as num?)?.toStringAsFixed(1) ?? '0')}%'),
                ),
              ),
              const SizedBox(height: 20),
              const Text('Leaderboard', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
              const SizedBox(height: 12),
              Expanded(
                child: lb.isNotEmpty
                    ? ListView.builder(
                        itemCount: lb.length,
                        itemBuilder: (c, i) {
                          final row = lb[i] as Map<String, dynamic>;
                          return Card(
                            child: ListTile(
                              leading: CircleAvatar(child: Text('${i + 1}')),
                              title: Text(row['name'] ?? row['waiter_id'] ?? 'Unknown'),
                              subtitle: Text('Tips: ${row['num_tips']} • Avg: ${(row['avg_rating'] as num?)?.toStringAsFixed(2) ?? '0'}'),
                            ),
                          );
                        },
                      )
                    : Center(child: Text(_loading ? 'Loading...' : 'No data yet')),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
