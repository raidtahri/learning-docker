import java.time.Instant;
import java.util.HashMap;
import java.util.Map;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@SpringBootApplication
public class App {
  public static void main(String[] args) {
    SpringApplication.run(App.class, args);
  }
}

@RestController
class ApiController {

  @Value("${app.name:java-app}")
  private String appName;

  @GetMapping("/")
  public Map<String, Object> root() {
    Map<String, Object> payload = new HashMap<>();
    payload.put("service", appName);
    payload.put("language", "java");
    payload.put("message", "Hello from Spring Boot");
    payload.put("timestamp", Instant.now().toString());
    return payload;
  }

  @GetMapping("/health")
  public Map<String, String> health() {
    Map<String, String> payload = new HashMap<>();
    payload.put("status", "ok");
    return payload;
  }
}

