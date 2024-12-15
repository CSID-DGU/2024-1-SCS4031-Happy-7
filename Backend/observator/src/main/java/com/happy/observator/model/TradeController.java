package com.happy.observator.model;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.time.Duration;
import java.time.LocalTime;
import java.time.format.DateTimeFormatter;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
// import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.ResponseBody;
import org.springframework.web.bind.annotation.RestController;

import com.happy.observator.service.UpbitService;
import com.happy.observator.service.UserService;
import com.happy.observator.Upbit.UpbitBalance;
import com.happy.observator.repository.OrderRepositary;

@Controller
public class TradeController {

    private final UserService userService;
    private final UpbitService upbitService;
    private final OrderRepositary orderRepository;
    private final ScheduledExecutorService scheduler = Executors.newScheduledThreadPool(1);
    // private final Map<LocalTime, S_Order> scheduledOrders = new ConcurrentHashMap<>();
    private Process pythonProcess;
    private boolean isAutoTrading = false;

    public TradeController(UserService userService, UpbitService upbitService, OrderRepositary orderRepositary){
        this.userService = userService;
        this.upbitService = upbitService;
        this.orderRepository = orderRepositary;
    }

    @GetMapping("/trade")
    public String showTradePage(@AuthenticationPrincipal UserDetails userDetails, Model model) {
        String username = userDetails.getUsername();
        User user = userService.findByUsername(username).orElseThrow(() -> new RuntimeException("User not found"));

        // Check if keys are present
        boolean hasKeys = user.getUpbitAccessKey() != null && user.getUpbitSecretKey() != null;

        if (hasKeys){
            try {
                List<UpbitBalance> balances = upbitService.getBalances(user.getUpbitAccessKey(), user.getUpbitSecretKey());
                model.addAttribute("balances", balances);
            } catch (Exception e) {
                model.addAttribute("errorMessage", "Failed to fetch balance: " + e.getMessage());
            }
        } else {
            model.addAttribute("errorMessage", "Please input your Upbit API keys to view balance.");
        }
        
        model.addAttribute("user", user);
        model.addAttribute("hasKeys", hasKeys);
        model.addAttribute("isAutoTrading", isAutoTrading);
        model.addAttribute("showForm", "form1");

        return "trade";  // Return the name of the template (trade.html)
    }

    @ResponseBody
    @PostMapping("/buy")
    public Map<String, Object> buyBitcoin(@AuthenticationPrincipal UserDetails userDetails, String price) {
        Map<String, Object> response = new HashMap<>();
        String username = userDetails.getUsername();
        User user = userService.findByUsername(username).orElseThrow(() -> new RuntimeException("User not found"));
        try {
            upbitService.placeBuyOrder(user.getUpbitAccessKey(), user.getUpbitSecretKey(), "KRW-BTC", price);
            response.put("success", true);
            response.put("message", "Buy order placed successfully");
        } catch (Exception e) {
            response.put("success", false);
            response.put("message", "Failed to place buy order: " + e.getMessage());
        }

        return response;  // Render the same page with success or error message
    }

    @ResponseBody
    @PostMapping("/sell")
    public Map<String, Object> sellBitcoin(@AuthenticationPrincipal UserDetails userDetails, String volume) {
        Map<String, Object> response = new HashMap<>();
        String username = userDetails.getUsername();
        User user = userService.findByUsername(username).orElseThrow(() -> new RuntimeException("User not found"));
        try {
            upbitService.placeSellOrder(user.getUpbitAccessKey(), user.getUpbitSecretKey(), "KRW-BTC", volume);
            response.put("success", true);
            response.put("message", "Sell order placed successfully");
        } catch (Exception e) {
            response.put("success", false);
            response.put("message", "Failed to place sell order: " + e.getMessage());
        }

        return response;  // Render the same page with success or error message
    }

    @PostMapping("/order")
    public String orderBitcoin(@AuthenticationPrincipal UserDetails userDetails, @RequestParam String action, @RequestParam String amount, Model model) {
        String username = userDetails.getUsername();
        User user = userService.findByUsername(username).orElseThrow(() -> new RuntimeException("User not found"));
        try {
            String response;
            if ("buy".equalsIgnoreCase(action)) {
                response = upbitService.placeBuyOrder(user.getUpbitAccessKey(), user.getUpbitSecretKey(), "KRW-BTC", amount);
                model.addAttribute("successMessage", "Buy order placed successfully: " + response);
            } else if ("sell".equalsIgnoreCase(action)) {
                response = upbitService.placeSellOrder(user.getUpbitAccessKey(), user.getUpbitSecretKey(), "KRW-BTC", amount);
                model.addAttribute("successMessage", "Sell order placed successfully: " + response);
            } else {
                model.addAttribute("errorMessage", "Invalid action. Please specify 'buy' or 'sell'.");
                return "redirect:/trade";
        }
        } catch (Exception e) {
            model.addAttribute("errorMessage", "Failed to place sell order: " + e.getMessage());
        }

        return "redirect:/trade";  // Render the same page with success or error message
    }

    /* all in schedule Order
    @PostMapping("/scheduleBuy")
    public String scheduleBuyBitcoin(@AuthenticationPrincipal UserDetails userDetails, @RequestParam("price") String price, @RequestParam String targetTime, Model model) {
        String username = userDetails.getUsername();
        User user = userService.findByUsername(username).orElseThrow(() -> new RuntimeException("User not found"));

        LocalTime target = LocalTime.parse(targetTime);
        LocalTime now = LocalTime.now();
        long delay = Duration.between(now, target).getSeconds();
        
        if (delay < 0) {
            model.addAttribute("errorMessage", "Target time has already passed.");
            return "trade";
        }

        scheduler.schedule(() -> {
            try {
                String response = upbitService.placeBuyOrder(user.getUpbitAccessKey(), user.getUpbitSecretKey(), "KRW-BTC", price);
                model.addAttribute("successMessage", "Buy order placed successfully at" + targetTime + ": " + response);
            } catch (Exception e) {
                model.addAttribute("errorMessage", "Failed to place buy order: " + e.getMessage());
            }
        }, delay, TimeUnit.SECONDS);

        return "redirect:/trade";  // Render the same page with success or error message
    }

    @PostMapping("/scheduleSell")
    public String scheduleSellBitcoin(@AuthenticationPrincipal UserDetails userDetails, @RequestParam("volume") String volume, @RequestParam String targetTime, Model model) {
        String username = userDetails.getUsername();
        User user = userService.findByUsername(username).orElseThrow(() -> new RuntimeException("User not found"));

        LocalTime target = LocalTime.parse(targetTime);
        LocalTime now = LocalTime.now();
        long delay = Duration.between(now, target).getSeconds();

        if (delay < 0) {
            model.addAttribute("errorMessage", "Target time has already passed.");
            return "trade";
        }

        scheduler.schedule(() -> {
            try {
                String response = upbitService.placeSellOrder(user.getUpbitAccessKey(), user.getUpbitSecretKey(), "KRW-BTC", volume);
                model.addAttribute("successMessage", "Sell order placed successfully at" + targetTime + ": " + response);
            } catch (Exception e) {
                model.addAttribute("errorMessage", "Failed to place sell order: " + e.getMessage());
            }
        }, delay, TimeUnit.SECONDS);

        return "redirect:/trade";  // Render the same page with success or error message
    }
    */
    @ResponseBody
    @PostMapping("/scheduleOrder")
    public Map<String, Object> scheduleOrderBitcoin(@AuthenticationPrincipal UserDetails userDetails, @RequestParam String action, @RequestParam String amount, @RequestParam String targetTime, Model model) {
        Map<String, Object> response = new HashMap<>();
        String username = userDetails.getUsername();
        User user = userService.findByUsername(username).orElseThrow(() -> new RuntimeException("User not found"));
        
        try{
            // Create a unique ID for the order
        String orderId = UUID.randomUUID().toString();

        // Check if there's an existing order for the target time and delete it
        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("HH:mm:ss.SSS");
        LocalTime target = LocalTime.parse(targetTime, formatter);
        Optional<S_Order> existingOrder = orderRepository.findByUserIdAndTargetTime(user.getId(), target);
        if (existingOrder.isPresent()) {
                orderRepository.delete(existingOrder.get());
                System.out.println("Deleted existing order: " + existingOrder);
        }

        // Save new order
        S_Order order = new S_Order(orderId, user.getId(), action, amount, "KRW-BTC", target);
        orderRepository.save(order);

        LocalTime now = LocalTime.now();
        long delay = Duration.between(now, target).toMillis();
        
        if (delay < 0) {
            response.put("success", false);
            response.put("message", "Target time has already passed.");
            return response;
        }

        scheduler.schedule(() -> executeOrder(order, user), delay, TimeUnit.MILLISECONDS);
        response.put("success", true);
        response.put("message", action + " order scheduled for " + targetTime);

        }catch (Exception e) {
        response.put("success", false);
        response.put("message", "Error scheduling order: " + e.getMessage());
        }
        return response;  // Render the same page with success or error message
    }

    private void executeOrder(S_Order order, User user) {
        if (order == null) return;  // No order to execute

        try {
            String response;
            if ("buy".equalsIgnoreCase(order.getAction())) {
                response = upbitService.placeBuyOrder(user.getUpbitAccessKey(), user.getUpbitSecretKey(), "KRW-BTC", order.getAmount());
                System.out.println("Buy order placed at " + order.getTargetTime() + ": " + response);
            } else if ("sell".equalsIgnoreCase(order.getAction())) {
                response = upbitService.placeSellOrder(user.getUpbitAccessKey(), user.getUpbitSecretKey(), "KRW-BTC", order.getAmount());
                System.out.println("Sell order placed at " + order.getTargetTime() + ": " + response);
            } else {
                System.out.println("Invalid action for order.");
            }
        } catch (Exception e) {
            System.err.println("Failed to place " + order.getAction() + " order at " + order.getTargetTime() + ": " + e.getMessage());
        }
    }

    @RestController
    @RequestMapping("/api/tradebalances")
    public class BalanceRestController {

        @Autowired
        private UserService userService;

        @Autowired
        private UpbitService upbitService;

        @GetMapping
        public ResponseEntity<?> getBalances(@AuthenticationPrincipal UserDetails userDetails) {
            String username = userDetails.getUsername();
            User user = userService.findByUsername(username).orElseThrow(() -> new RuntimeException("User not found"));

            // Check if keys are present
            if (user.getUpbitAccessKey() != null && user.getUpbitSecretKey() != null) {
                try {
                    List<UpbitBalance> balances = upbitService.getBalances(user.getUpbitAccessKey(), user.getUpbitSecretKey());
                    //System.out.println(balances);
                    return ResponseEntity.ok(balances);
                } catch (Exception e) {
                    return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body("Failed to fetch balances: " + e.getMessage());
                }
            } else {
                return ResponseEntity.status(HttpStatus.BAD_REQUEST).body("API keys are missing.");
            }
        }
    }

    @ResponseBody
    @PostMapping("/start")
    private Map<String, Object> startTrade(@AuthenticationPrincipal UserDetails userDetails, @RequestParam("ThresholdLevel") float thresholdLevel) {
        Map<String, Object> response = new HashMap<>();

        try {
            String username = userDetails.getUsername();
            User user = userService.findByUsername(username).orElseThrow(() -> new RuntimeException("User not found"));
            float threshold = thresholdLevel;
            System.out.println("Received Threshold level: " + threshold + ". User ID: " + user.getId());

            response.put("success", true);

            // Python 스크립트를 실행
            ProcessBuilder processBuilder = new ProcessBuilder(
                "python3",
                "/home/ubuntu/project/OBservator/Backend/observator/python/trade.py",
                String.valueOf(threshold),
                String.valueOf(user.getId()) // User ID 추가
            );
            processBuilder.redirectErrorStream(true);
            pythonProcess = processBuilder.start();

            // Python 출력 로그 읽기
            new Thread(() -> {
                try (BufferedReader reader = new BufferedReader(new InputStreamReader(pythonProcess.getInputStream()))) {
                    String line;
                    while ((line = reader.readLine()) != null) {
                        System.out.println("[Python Log]: " + line);
                    }
                } catch (Exception e) {
                    System.err.println("Error reading Python script output: " + e.getMessage());
                }
            }).start();

            // service.sh 실행
            new Thread(() -> {
                try {
                    ProcessBuilder bashProcessBuilder = new ProcessBuilder(
                        "bash",
                        "/home/ubuntu/project/OBservator/Backend/observator/src/main/java/com/happy/observator/server/service.sh"
                    );
                    bashProcessBuilder.redirectErrorStream(true);
                    Process bashProcess = bashProcessBuilder.start();

                    // Bash 스크립트 출력 로그 읽기
                    try (BufferedReader reader = new BufferedReader(new InputStreamReader(bashProcess.getInputStream()))) {
                        String line;
                        while ((line = reader.readLine()) != null) {
                            System.out.println("[Bash Log]: " + line);
                        }
                    }
                } catch (Exception e) {
                    System.err.println("Failed to execute service.sh: " + e.getMessage());
                }
            }).start();

            // 상태 업데이트
            isAutoTrading = true;
            // response.put("newThreshold", thresholdLevel);
        } catch (Exception e) {
            response.put("success", false);
            response.put("error", e.getMessage());
            System.err.println("Failed to start Python script: " + e.getMessage());
        }

        //model.addAttribute("isAutoTrading", isAutoTrading); // 상태 전달
        return response;
    }

    @ResponseBody
    @PostMapping("/change")
    private Map<String, Object> changeTrade(@AuthenticationPrincipal UserDetails userDetails, @RequestParam("ThresholdLevel") float thresholdLevel) {
        Map<String, Object> response = new HashMap<>();
        try{
            String username = userDetails.getUsername();
            User user = userService.findByUsername(username).orElseThrow(() -> new RuntimeException("User not found"));
            float threshold = thresholdLevel;
            System.out.println("Received Threshold level: " + threshold + ". User ID: " + user.getId());
            
            response.put("success", true);

            //Python 관련 집어넣는 곳

            //response.put("newThreshold", thresholdLevel);
        } catch (Exception e){
            response.put("success", false);
            response.put("error", e.getMessage());
        }
        
        return response;
    }

    @ResponseBody
    @PostMapping("/end")
    private Map<String, Object> endTrade(@AuthenticationPrincipal UserDetails userDetails, Model model) {
        Map<String, Object> response = new HashMap<>();

        // Python 프로세스 종료
        if (pythonProcess != null && pythonProcess.isAlive()) {
            pythonProcess.destroy();
            System.out.println("Python script stopped successfully.");
        } else {
            System.out.println("No Python script is currently running.");
        }

        try {
            String username = userDetails.getUsername();
            User user = userService.findByUsername(username).orElseThrow(() -> new RuntimeException("User not found"));
            System.out.println("End Trade User ID: " + user.getId());

            response.put("success", true);

            // 특정 SSH 프로세스 종료
            String killCommand = "ps -ef | grep 'ssh -v fairy@14.32.188.229' | grep -v grep | awk '{print $2}' | xargs kill -9";
            ProcessBuilder killProcessBuilder = new ProcessBuilder("bash", "-c", killCommand);
            Process killProcess = killProcessBuilder.start();
            killProcess.waitFor(); // 종료될 때까지 대기
            System.out.println("SSH process stopped successfully.");

            // 상태 업데이트
            isAutoTrading = false;
        } catch (Exception e) {
            response.put("success", false);
            response.put("error", e.getMessage());
            System.err.println("Failed to stop SSH process: " + e.getMessage());
        }

        //model.addAttribute("isAutoTrading", isAutoTrading); // 상태 전달
        return response;
    }
}
