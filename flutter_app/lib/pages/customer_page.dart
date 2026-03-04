import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/api.dart';
import '../main.dart';

class CustomerPage extends StatefulWidget {
  const CustomerPage({super.key});

  @override
  State<CustomerPage> createState() => _CustomerPageState();
}

class _CustomerPageState extends State<CustomerPage> {
  final _amountCtl = TextEditingController();
  final _feedbackCtl = TextEditingController();
  int _rating = 5;
  String _waiterId = '';
  bool _submitting = false;
  bool _loadingWaiters = false;
  List<String> _waiterOptions = [];

  @override
  void dispose() {
    _amountCtl.dispose();
    _feedbackCtl.dispose();
    super.dispose();
  }

  Future<void> _loadWaiters() async {
    setState(() {
      _loadingWaiters = true;
    });
    final list = await api.getWaiters();
    setState(() {
      _waiterOptions = list.map((e) => e['waiter_id'] as String).toList();
      _loadingWaiters = false;
    });
  }

  void _submit() async {
    final amt = double.tryParse(_amountCtl.text) ?? 0.0;
    if (_waiterId.isEmpty || amt <= 0) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(
        content: Text('Provide waiter ID and amount > 0'),
        backgroundColor: Colors.red,
      ));
      return;
    }
    setState(() => _submitting = true);
    final resp = await api.submitTip(_waiterId, amt, _rating, _feedbackCtl.text);
    setState(() => _submitting = false);
    if (resp != null) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(
        content: Text('✓ Tip submitted successfully'),
        backgroundColor: Colors.green,
      ));
      _amountCtl.clear();
      _feedbackCtl.clear();
      setState(() => _rating = 5);
    } else {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(
        content: Text('✗ Submission failed. Check backend is running.'),
        backgroundColor: Colors.red,
      ));
    }
  }

  @override
  void initState() {
    super.initState();
    _loadWaiters();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Customer · TipTrack')),
      body: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 12.0),
        child: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              if (_loadingWaiters) const LinearProgressIndicator(),
              DropdownButtonFormField<String>(
                initialValue: _waiterId.isNotEmpty ? _waiterId : null,
                items: _waiterOptions
                    .map((w) => DropdownMenuItem(value: w, child: Text(w)))
                    .toList(),
                onChanged: (v) => setState(() => _waiterId = v ?? ''),
                decoration: const InputDecoration(labelText: 'Waiter ID'),
              ),
              const SizedBox(height: 12),
              TextField(controller: _amountCtl, keyboardType: TextInputType.number, decoration: const InputDecoration(labelText: 'Amount')),
              const SizedBox(height: 12),
              const Text('Rating'),
              Slider(value: _rating.toDouble(), min: 1, max: 5, divisions: 4, label: '$_rating', onChanged: (v) => setState(() => _rating = v.toInt())),
              const SizedBox(height: 12),
              TextField(controller: _feedbackCtl, maxLines: 4, decoration: const InputDecoration(labelText: 'Feedback (optional)')),
              const SizedBox(height: 16),
              _submitting
                  ? const Center(child: CircularProgressIndicator())
                  : ElevatedButton(onPressed: _submit, child: const Text('Submit Tip')),
            ],
          ),
        ),
      ),
      drawer: Drawer(
        child: ListView(children: [
          ListTile(title: const Text('Waiter Dashboard'), onTap: () => Navigator.pushNamed(context, '/waiter')),
          ListTile(title: const Text('Owner Dashboard'), onTap: () => Navigator.pushNamed(context, '/owner')),
          ListTile(title: const Text('Admin QR'), onTap: () => Navigator.pushNamed(context, '/admin')),
          ListTile(title: const Text('AI Assistant'), onTap: () => Navigator.pushNamed(context, '/ai')),
          ListTile(title: const Text('Sign out'), onTap: () {
            Provider.of<AuthModel>(context, listen: false).clear();
            Navigator.pushReplacementNamed(context, '/login');
          }),
        ]),
      ),
    );
  }
}
