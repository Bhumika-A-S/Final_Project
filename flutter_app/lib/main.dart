import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'pages/customer_page.dart';
import 'pages/waiter_dashboard_page.dart';
import 'pages/owner_dashboard_page.dart';
import 'pages/admin_page.dart';
import 'pages/login_page.dart';
import 'pages/ai_assistant_page.dart';
import 'services/api.dart';

void main() {
  runApp(const TipTrackApp());
}

class AuthModel extends ChangeNotifier {
  String? token;
  String? role;
  String? username;
  String? waiterId;

  void update({String? t, String? r, String? u, String? w}) {
    token = t ?? token;
    role = r ?? role;
    username = u ?? username;
    waiterId = w ?? waiterId;
    notifyListeners();
  }

  void clear() {
    token = null;
    role = null;
    waiterId = null;
    notifyListeners();
  }
}

class TipTrackApp extends StatelessWidget {
  const TipTrackApp({super.key});

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider(
      create: (_) => AuthModel(),
      child: Consumer<AuthModel>(
        builder: (ctx, auth, _) {
          // keep API client token in sync
          api.setToken(auth.token);

          return MaterialApp(
            title: 'TipTrack',
            theme: ThemeData(primarySwatch: Colors.blue),
            home: auth.token == null ? const LoginPage() : const CustomerPage(),
            routes: {
              '/login': (_) => const LoginPage(),
              '/waiter': (_) => const WaiterDashboardPage(),
              '/owner': (_) => const OwnerDashboardPage(),
              '/admin': (_) => const AdminPage(),
              '/ai': (_) => const AiAssistantPage(),
            },
          );
        },
      ),
    );
  }
}
