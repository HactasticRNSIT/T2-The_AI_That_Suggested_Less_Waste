$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$html = Get-Content -Raw -Path (Join-Path $root "ecowise_static_preview.html")
$body = [System.Text.Encoding]::UTF8.GetBytes($html)
$headerText = "HTTP/1.1 200 OK`r`nContent-Type: text/html; charset=utf-8`r`nContent-Length: $($body.Length)`r`nConnection: close`r`n`r`n"
$header = [System.Text.Encoding]::ASCII.GetBytes($headerText)

$server = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Parse("127.0.0.1"), 5000)
$server.Start()
Write-Host "EcoWise preview running at http://127.0.0.1:5000/"

while ($true) {
  $client = $server.AcceptTcpClient()
  $stream = $client.GetStream()
  $buffer = New-Object byte[] 1024
  $null = $stream.Read($buffer, 0, $buffer.Length)
  $stream.Write($header, 0, $header.Length)
  $stream.Write($body, 0, $body.Length)
  $stream.Close()
  $client.Close()
}
