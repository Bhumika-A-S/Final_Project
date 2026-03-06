import 'package:flutter/material.dart';
import '../services/api.dart';
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

  Future<void> login() async {

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

    // WAITER LOGIN
    if (role == "waiter") {

      Navigator.pushReplacement(
        context,
        MaterialPageRoute(
          builder: (context) =>
             WaiterDashboardPage(),
        ),
      );

    }

    // OWNER LOGIN
    else if (role == "owner") {

      Navigator.pushReplacement(
        context,
        MaterialPageRoute(
          builder: (context) => OwnerDashboardPage(),
        ),
      );

    }

    // ADMIN LOGIN
    else if (role == "admin") {

      Navigator.pushReplacement(
        context,
        MaterialPageRoute(
          builder: (context) => AdminPage(),
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
              obscureText: true,
              decoration: const InputDecoration(
                labelText: "Password",
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