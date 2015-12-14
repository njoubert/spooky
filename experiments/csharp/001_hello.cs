using System;
using System.Net;
using System.Net.Sockets;
using System.Threading;
using System.Text;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

public class HelloWorld
{

   	public static IPEndPoint e;
	public static UdpClient u;

    static public void Main ()
    {
        Console.WriteLine ("STARTING UP");
        ReceiveMessages();
    }

	public static void ReceiveCallback(IAsyncResult ar)
	{

	  Byte[] receiveBytes = u.EndReceive(ar, ref e);
	  string receiveString = Encoding.ASCII.GetString(receiveBytes);

	  //Console.WriteLine("Received: {0}", receiveString);

	  dynamic jsonVal = JObject.Parse(receiveString);
	  dynamic attitude = jsonVal.GetValue("127.0.0.1").GetValue("ATTITUDE");
	  dynamic yaw_radians = attitude.yaw;
	  dynamic yaw_degrees = yaw_radians * 57.2958;
	  Console.WriteLine("  yaw = " + yaw_degrees + " degrees");

	  u.BeginReceive(new AsyncCallback(ReceiveCallback), null);

	}

	public static void ReceiveMessages()
	{
	  // Receive a message and write it to the console.
	  e = new IPEndPoint(IPAddress.Any, 19000);
	  u = new UdpClient(e);

	  Console.WriteLine("listening for messages");
	  u.BeginReceive(new AsyncCallback(ReceiveCallback), null);

	  // Do some work while we wait for a message. For this example,
	  // we'll just sleep
	  while (true)
	  {
	    Thread.Sleep(100);
	  }
	}
}