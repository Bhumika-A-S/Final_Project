import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:provider/provider.dart';

import '../services/api.dart';
import '../main.dart';

import 'waiter_dashboard_page.dart';
import 'owner_dashboard_page.dart';
import 'admin_page.dart';

class LoginPage extends StatefulWidget {
  const LoginPage({super.key});

  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {

  final TextEditingController usernameController = TextEditingController();
  final TextEditingController passwordController = TextEditingController();

  bool loading = false;
  bool hidePassword = true;

  Future<void> login() async {

    // Validate input
    if (usernameController.text.isEmpty || passwordController.text.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("Enter username and password")),
      );
      return;
    }

    setState(() {
      loading = true;
    });

    final result = await api.login(
      usernameController.text,
      passwordController.text,
    );

    setState(() {
      loading = false;
    });

    if (result == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("Login failed")),
      );
      return;
    }

    String role = result["role"];
    String token = result["access_token"];

    // Save token in API client
    api.setToken(token);
    api.role = role;

    // Save locally
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString("token", token);
    await prefs.setString("role", role);

    // Update provider
    Provider.of<AuthModel>(context, listen: false).update(
      t: token,
      r: role,
      u: usernameController.text,
    );

    // Navigate based on role
    if (role == "waiter") {

      Navigator.pushReplacement(
        context,
        MaterialPageRoute(
          builder: (_) => const WaiterDashboardPage(),
        ),
      );

    } else if (role == "owner") {

      Navigator.pushReplacement(
        context,
        MaterialPageRoute(
          builder: (_) => const OwnerDashboardPage(),
        ),
      );

    } else if (role == "admin") {

      Navigator.pushReplacement(
        context,
        MaterialPageRoute(
          builder: (_) => const AdminPage(),
        ),
      );

    }
  }

  @override
  Widget build(BuildContext context) {

    return Scaffold(

      appBar: AppBar(
        title: const Text("TipTrack Login"),
      ),

      body: Padding(
        padding: const EdgeInsets.all(20),

        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [

            TextField(
              controller: usernameController,
              decoration: const InputDecoration(
                labelText: "Username",
              ),
            ),

            const SizedBox(height: 10),

            TextField(
              controller: passwordController,
              obscureText: hidePassword,
              decoration: InputDecoration(
                labelText: "Password",
                suffixIcon: IconButton(
                  icon: Icon(
                    hidePassword
                        ? Icons.visibility
                        : Icons.visibility_off,
                  ),
                  onPressed: () {
                    setState(() {
                      hidePassword = !hidePassword;
                    });
                  },
                ),
              ),
            ),

            const SizedBox(height: 20),

            loading
                ? const CircularProgressIndicator()
                : ElevatedButton(
                    onPressed: login,
                    child: const Text("Login"),
                  ),

          ],
        ),
      ),
    );
  }
}