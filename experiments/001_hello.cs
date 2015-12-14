using System;
using System.Net;
using System.Net.Sockets;
using System.Threading;
using System.Text;

public class HelloWorld
{
    public static bool messageReceived = false;

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

	  Console.WriteLine("Received: {0}", receiveString);

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