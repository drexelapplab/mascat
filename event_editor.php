<html>
	<head>
	</head>
	
	<body>
		<?php
			echo "<html><body><table>\n\n";
			$f = fopen("so-csv.csv", "r");
			while (($line = fgetcsv($f)) !== false) {
        			echo "<tr>";
        			foreach ($line as $cell) {
                			echo "<td>" . htmlspecialchars($cell) . "</td>";
        			}
        			echo "</tr>\n";
			}
			fclose($f);
			echo "\n</table></body></html>";
		?>
	</body>
</html>
