import 'package:flutter/material.dart';
import '../services/api.dart';
import 'login_page.dart';

class OwnerDashboardPage extends StatefulWidget {
  const OwnerDashboardPage({super.key});

  @override
  State<OwnerDashboardPage> createState() => _OwnerDashboardPageState();
}

class _OwnerDashboardPageState extends State<OwnerDashboardPage> {

  Map<String, dynamic>? _team;
  bool _loading = false;
  String? _error;

  @override
  void initState() {
    super.initState();

    // RBAC check
    if (api.role != "owner") {
      Future.microtask(() {
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(builder: (_) => const LoginPage()),
        );
      });
      return;
    }

    _load();
  }

  Future<void> _load() async {
    setState(() {
      _loading = true;
      _error = null;
    });

    try {
      final data = await api.getTeamInsights();

      setState(() {
        _team = data;
      });

    } catch (e) {
      setState(() {
        _error = "Error loading team insights";
      });
    }

    setState(() {
      _loading = false;
    });
  }

  @override
  Widget build(BuildContext context) {

    final lb = _team?['leaderboard'] as List? ?? [];

    return Scaffold(
      appBar: AppBar(title: const Text("Owner Dashboard")),

      body: RefreshIndicator(
        onRefresh: _load,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [

            if (_loading) const LinearProgressIndicator(),

            if (_error != null)
              Text(_error!, style: const TextStyle(color: Colors.red)),

            const SizedBox(height: 20),

            ListTile(
              title: const Text("Total Orders"),
              subtitle: Text('${_team?['total_orders'] ?? 0}'),
            ),

            ListTile(
              title: const Text("Overall Score"),
              subtitle: Text('${_team?['overall_score'] ?? 0} / 100'),
            ),

            ListTile(
              title: const Text("Low Ratings %"),
              subtitle: Text('${_team?['pct_low_ratings'] ?? 0}%'),
            ),

            const SizedBox(height: 20),

            const Text("Leaderboard", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),

            for (var w in lb)
              ListTile(
                title: Text(w['waiter_id'] ?? ''),
                subtitle: Text("Score: ${w['score'] ?? 0}"),
              ),
          ],
        ),
      ),
    );
  }
}