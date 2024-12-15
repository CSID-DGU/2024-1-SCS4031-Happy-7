<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>Upbit Balance Information</title>
</head>
<body style="font-family: Arial, sans-serif; background-color: #f9f9f9; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; flex-direction: column;">
    <div style="font-size: 16px; color: #555; margin-bottom: 30px; text-align: center;">${username}님의 업비트 자산 정보를 알려드립니다.</div>

    <table style="width: 50%; margin: 10px auto; border-collapse: collapse; background-color: #ffffff; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1); border-radius: 10px; overflow: hidden;">
        <thead>
            <tr>
                <th style="padding: 15px; border: 1px solid #ddd; text-align: center; background-color: #007BFF; color: white; font-weight: bold;">Currency</th>
                <th style="padding: 15px; border: 1px solid #ddd; text-align: center; background-color: #007BFF; color: white; font-weight: bold;">Balance</th>
                <th style="padding: 15px; border: 1px solid #ddd; text-align: center; background-color: #007BFF; color: white; font-weight: bold;">Avg Buy Price</th>
            </tr>
        </thead>
        <tbody>
            <#list balances as balance>
                <tr style="background-color: #f2f2f2;">
                    <td style="padding: 15px; border: 1px solid #ddd; text-align: center;">${balance.currency}</td>
                    <td style="padding: 15px; border: 1px solid #ddd; text-align: center;">${balance.balance}</td>
                    <td style="padding: 15px; border: 1px solid #ddd; text-align: center;">${balance.avgBuyPrice}</td>
                </tr>
            </#list>
        </tbody>
    </table>

    <div style="margin-top: 20px; font-size: 14px; color: #888; text-align: center;">
        <p>OBservator를 이용해 주셔서 감사합니다.</p>
        <p>본 이메일은 발신 전용이며, 회신은 불가합니다.</p>
    </div>
</body>
</html>
